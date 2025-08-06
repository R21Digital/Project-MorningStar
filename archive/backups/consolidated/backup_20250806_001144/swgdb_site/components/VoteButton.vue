<template>
  <div class="vote-button-container">
    <!-- Vote Summary Display -->
    <div class="vote-summary" v-if="showSummary">
      <div class="vote-stats">
        <span class="vote-count">{{ summary.total_votes }} votes</span>
        <span class="vote-score" :class="scoreClass">{{ summary.score }}</span>
      </div>
      <div class="vote-breakdown">
        <span class="thumbs-up-count">👍 {{ summary.thumbs_up }}</span>
        <span class="thumbs-down-count">👎 {{ summary.thumbs_down }}</span>
        <span class="neutral-count" v-if="summary.neutral > 0">➖ {{ summary.neutral }}</span>
      </div>
    </div>

    <!-- Vote Buttons -->
    <div class="vote-buttons">
      <button
        class="vote-btn thumbs-up"
        :class="{ active: userVote === 'thumbs_up', disabled: loading }"
        @click="submitVote('thumbs_up')"
        :disabled="loading"
        :title="getVoteTooltip('thumbs_up')"
      >
        <span class="vote-icon">👍</span>
        <span class="vote-text" v-if="showLabels">Thumbs Up</span>
      </button>

      <button
        class="vote-btn neutral"
        :class="{ active: userVote === 'neutral', disabled: loading }"
        @click="submitVote('neutral')"
        :disabled="loading"
        :title="getVoteTooltip('neutral')"
      >
        <span class="vote-icon">➖</span>
        <span class="vote-text" v-if="showLabels">Neutral</span>
      </button>

      <button
        class="vote-btn thumbs-down"
        :class="{ active: userVote === 'thumbs_down', disabled: loading }"
        @click="submitVote('thumbs_down')"
        :disabled="loading"
        :title="getVoteTooltip('thumbs_down')"
      >
        <span class="vote-icon">👎</span>
        <span class="vote-text" v-if="showLabels">Thumbs Down</span>
      </button>
    </div>

    <!-- Feedback Modal -->
    <div class="feedback-modal" v-if="showFeedbackModal" @click="closeFeedbackModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Vote Feedback</h3>
          <button class="close-btn" @click="closeFeedbackModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="vote-reason">Reason for your vote (optional):</label>
            <textarea
              id="vote-reason"
              v-model="feedbackForm.reason"
              placeholder="Why did you vote this way?"
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="vote-feedback">Additional feedback (optional):</label>
            <textarea
              id="vote-feedback"
              v-model="feedbackForm.feedback"
              placeholder="Any additional comments or suggestions?"
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeFeedbackModal">Cancel</button>
          <button class="btn btn-primary" @click="confirmVote" :disabled="submitting">
            {{ submitting ? 'Submitting...' : 'Submit Vote' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div class="error-message" v-if="error">
      <span class="error-icon">⚠️</span>
      <span>{{ error }}</span>
      <button class="dismiss-btn" @click="clearError">×</button>
    </div>

    <!-- Success Message -->
    <div class="success-message" v-if="successMessage">
      <span class="success-icon">✅</span>
      <span>{{ successMessage }}</span>
      <button class="dismiss-btn" @click="clearSuccess">×</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VoteButton',
  props: {
    contentType: {
      type: String,
      required: true,
      validator: value => ['build', 'guide', 'profile', 'comment'].includes(value)
    },
    contentId: {
      type: String,
      required: true
    },
    voterDiscordId: {
      type: String,
      default: null
    },
    showSummary: {
      type: Boolean,
      default: true
    },
    showLabels: {
      type: Boolean,
      default: false
    },
    compact: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      summary: {
        total_votes: 0,
        thumbs_up: 0,
        thumbs_down: 0,
        neutral: 0,
        score: 0,
        popularity_rank: 0,
        last_updated: null
      },
      userVote: null,
      loading: false,
      submitting: false,
      error: null,
      successMessage: null,
      showFeedbackModal: false,
      pendingVoteType: null,
      feedbackForm: {
        reason: '',
        feedback: ''
      }
    }
  },
  computed: {
    scoreClass() {
      if (this.summary.score > 0) return 'positive'
      if (this.summary.score < 0) return 'negative'
      return 'neutral'
    }
  },
  mounted() {
    this.loadVoteData()
  },
  methods: {
    async loadVoteData() {
      try {
        this.loading = true
        
        // Load vote summary
        const summaryResponse = await fetch(`/api/votes/summary/${this.contentType}/${this.contentId}`)
        const summaryData = await summaryResponse.json()
        
        if (summaryData.success) {
          this.summary = summaryData.summary
        }
        
        // Load user's vote
        const userVoteResponse = await fetch(`/api/votes/user-vote/${this.contentType}/${this.contentId}`)
        const userVoteData = await userVoteResponse.json()
        
        if (userVoteData.success && userVoteData.vote) {
          this.userVote = userVoteData.vote.vote_type
        }
        
      } catch (error) {
        console.error('Error loading vote data:', error)
        this.showError('Failed to load vote data')
      } finally {
        this.loading = false
      }
    },
    
    async submitVote(voteType) {
      if (this.loading) return
      
      this.pendingVoteType = voteType
      this.showFeedbackModal = true
    },
    
    async confirmVote() {
      try {
        this.submitting = true
        
        const voteData = {
          content_type: this.contentType,
          content_id: this.contentId,
          vote_type: this.pendingVoteType,
          voter_discord_id: this.voterDiscordId,
          reason: this.feedbackForm.reason,
          feedback: this.feedbackForm.feedback
        }
        
        const response = await fetch('/api/votes/submit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(voteData)
        })
        
        const data = await response.json()
        
        if (data.success) {
          this.userVote = this.pendingVoteType
          this.showSuccess(data.message)
          this.closeFeedbackModal()
          await this.loadVoteData() // Refresh summary
        } else {
          this.showError(data.error || 'Failed to submit vote')
        }
        
      } catch (error) {
        console.error('Error submitting vote:', error)
        this.showError('Failed to submit vote')
      } finally {
        this.submitting = false
      }
    },
    
    closeFeedbackModal() {
      this.showFeedbackModal = false
      this.pendingVoteType = null
      this.feedbackForm.reason = ''
      this.feedbackForm.feedback = ''
    },
    
    getVoteTooltip(voteType) {
      const tooltips = {
        thumbs_up: 'Vote thumbs up',
        neutral: 'Vote neutral',
        thumbs_down: 'Vote thumbs down'
      }
      return tooltips[voteType] || ''
    },
    
    showError(message) {
      this.error = message
      setTimeout(() => {
        this.clearError()
      }, 5000)
    },
    
    showSuccess(message) {
      this.successMessage = message
      setTimeout(() => {
        this.clearSuccess()
      }, 3000)
    },
    
    clearError() {
      this.error = null
    },
    
    clearSuccess() {
      this.successMessage = null
    }
  }
}
</script>

<style scoped>
.vote-button-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.vote-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.vote-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.vote-count {
  font-size: 14px;
  color: #a0a0a0;
  font-weight: 500;
}

.vote-score {
  font-size: 18px;
  font-weight: bold;
  padding: 4px 8px;
  border-radius: 4px;
}

.vote-score.positive {
  color: #4ade80;
  background: rgba(74, 222, 128, 0.1);
}

.vote-score.negative {
  color: #f87171;
  background: rgba(248, 113, 113, 0.1);
}

.vote-score.neutral {
  color: #a0a0a0;
  background: rgba(160, 160, 160, 0.1);
}

.vote-breakdown {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #a0a0a0;
}

.thumbs-up-count {
  color: #4ade80;
}

.thumbs-down-count {
  color: #f87171;
}

.neutral-count {
  color: #a0a0a0;
}

.vote-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.vote-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
  min-width: 60px;
}

.vote-btn:hover:not(.disabled) {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.vote-btn.active {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.2);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
}

.vote-btn.thumbs-up.active {
  border-color: #4ade80;
  background: rgba(74, 222, 128, 0.2);
  box-shadow: 0 0 0 2px rgba(74, 222, 128, 0.3);
}

.vote-btn.thumbs-down.active {
  border-color: #f87171;
  background: rgba(248, 113, 113, 0.2);
  box-shadow: 0 0 0 2px rgba(248, 113, 113, 0.3);
}

.vote-btn.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.vote-icon {
  font-size: 20px;
}

.vote-text {
  font-size: 10px;
  text-align: center;
}

/* Compact mode */
.vote-button-container.compact .vote-buttons {
  flex-direction: row;
}

.vote-button-container.compact .vote-btn {
  flex-direction: row;
  min-width: auto;
  padding: 6px 10px;
}

.vote-button-container.compact .vote-text {
  display: none;
}

/* Feedback Modal */
.feedback-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 12px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h3 {
  margin: 0;
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #a0a0a0;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.modal-body {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #ffffff;
  font-weight: 500;
  font-size: 14px;
}

.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-family: inherit;
  font-size: 14px;
  resize: vertical;
  transition: border-color 0.3s ease;
}

.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
}

.form-group textarea::placeholder {
  color: #a0a0a0;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Messages */
.error-message,
.success-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  position: relative;
}

.error-message {
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #f87171;
}

.success-message {
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.3);
  color: #4ade80;
}

.dismiss-btn {
  background: none;
  border: none;
  color: inherit;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
  margin-left: auto;
}

.dismiss-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* Responsive Design */
@media (max-width: 480px) {
  .vote-buttons {
    gap: 4px;
  }
  
  .vote-btn {
    padding: 6px 8px;
    min-width: 50px;
  }
  
  .vote-icon {
    font-size: 16px;
  }
  
  .modal-content {
    padding: 16px;
    width: 95%;
  }
}
</style> 