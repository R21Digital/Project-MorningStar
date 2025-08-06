import React, { useState, useEffect } from 'react';
import './BuildFeedbackPanel.css';

interface VoteSummary {
  content_type: string;
  content_id: string;
  total_votes: number;
  thumbs_up: number;
  thumbs_down: number;
  neutral: number;
  score: number;
  popularity_rank: number;
  last_updated: string;
}

interface UserVote {
  vote_id: string;
  vote_type: string;
  reason: string;
  feedback: string;
  created_at: string;
  updated_at: string;
}

interface Comment {
  id: string;
  author: string;
  author_discord_id: string;
  content: string;
  created_at: string;
  is_creator_reply: boolean;
  parent_comment_id?: string;
  replies: Comment[];
}

interface BuildFeedbackPanelProps {
  contentType: 'build' | 'guide' | 'profile' | 'comment';
  contentId: string;
  contentTitle: string;
  creatorDiscordId?: string;
  voterDiscordId?: string;
  showComments?: boolean;
  showVoteSummary?: boolean;
}

const BuildFeedbackPanel: React.FC<BuildFeedbackPanelProps> = ({
  contentType,
  contentId,
  contentTitle,
  creatorDiscordId,
  voterDiscordId,
  showComments = true,
  showVoteSummary = true
}) => {
  const [voteSummary, setVoteSummary] = useState<VoteSummary | null>(null);
  const [userVote, setUserVote] = useState<UserVote | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  // Vote modal state
  const [showVoteModal, setShowVoteModal] = useState(false);
  const [pendingVoteType, setPendingVoteType] = useState<string | null>(null);
  const [voteForm, setVoteForm] = useState({
    reason: '',
    feedback: ''
  });
  
  // Comment state
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState<string | null>(null);
  const [replyContent, setReplyContent] = useState('');

  useEffect(() => {
    loadFeedbackData();
  }, [contentType, contentId]);

  const loadFeedbackData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load vote summary
      const summaryResponse = await fetch(`/api/votes/summary/${contentType}/${contentId}`);
      const summaryData = await summaryResponse.json();
      
      if (summaryData.success) {
        setVoteSummary(summaryData.summary);
      }

      // Load user's vote
      const userVoteResponse = await fetch(`/api/votes/user-vote/${contentType}/${contentId}`);
      const userVoteData = await userVoteResponse.json();
      
      if (userVoteData.success && userVoteData.vote) {
        setUserVote(userVoteData.vote);
      }

      // Load comments (placeholder - would need comment API)
      // const commentsResponse = await fetch(`/api/comments/${contentType}/${contentId}`);
      // const commentsData = await commentsResponse.json();
      // if (commentsData.success) {
      //   setComments(commentsData.comments);
      // }

    } catch (err) {
      setError('Failed to load feedback data');
      console.error('Error loading feedback data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVoteClick = (voteType: string) => {
    setPendingVoteType(voteType);
    setShowVoteModal(true);
  };

  const submitVote = async () => {
    if (!pendingVoteType) return;

    try {
      setSubmitting(true);
      
      const voteData = {
        content_type: contentType,
        content_id: contentId,
        vote_type: pendingVoteType,
        voter_discord_id: voterDiscordId,
        reason: voteForm.reason,
        feedback: voteForm.feedback
      };

      const response = await fetch('/api/votes/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(voteData)
      });

      const data = await response.json();

      if (data.success) {
        setUserVote({
          vote_id: data.vote_id,
          vote_type: pendingVoteType,
          reason: voteForm.reason,
          feedback: voteForm.feedback,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });
        setSuccessMessage(data.message);
        setShowVoteModal(false);
        resetVoteForm();
        await loadFeedbackData(); // Refresh summary
      } else {
        setError(data.error || 'Failed to submit vote');
      }

    } catch (err) {
      setError('Failed to submit vote');
      console.error('Error submitting vote:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const submitComment = async () => {
    if (!newComment.trim()) return;

    try {
      setSubmitting(true);
      
      // Placeholder for comment submission
      const commentData = {
        content_type: contentType,
        content_id: contentId,
        content: newComment,
        author_discord_id: voterDiscordId,
        parent_comment_id: replyingTo
      };

      // const response = await fetch('/api/comments/submit', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(commentData)
      // });

      // Simulate comment submission
      const newCommentObj: Comment = {
        id: Date.now().toString(),
        author: 'User',
        author_discord_id: voterDiscordId || '',
        content: newComment,
        created_at: new Date().toISOString(),
        is_creator_reply: false,
        replies: []
      };

      if (replyingTo) {
        // Add reply to existing comment
        setComments(prev => prev.map(comment => 
          comment.id === replyingTo 
            ? { ...comment, replies: [...comment.replies, newCommentObj] }
            : comment
        ));
        setReplyingTo(null);
        setReplyContent('');
      } else {
        // Add new top-level comment
        setComments(prev => [newCommentObj, ...prev]);
      }

      setNewComment('');
      setSuccessMessage('Comment submitted successfully');

    } catch (err) {
      setError('Failed to submit comment');
      console.error('Error submitting comment:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const resetVoteForm = () => {
    setVoteForm({ reason: '', feedback: '' });
    setPendingVoteType(null);
  };

  const getVoteIcon = (voteType: string) => {
    switch (voteType) {
      case 'thumbs_up': return '👍';
      case 'thumbs_down': return '👎';
      case 'neutral': return '➖';
      default: return '❓';
    }
  };

  const getVoteColor = (voteType: string) => {
    switch (voteType) {
      case 'thumbs_up': return '#4ade80';
      case 'thumbs_down': return '#f87171';
      case 'neutral': return '#a0a0a0';
      default: return '#ffffff';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const clearMessages = () => {
    setError(null);
    setSuccessMessage(null);
  };

  if (loading) {
    return (
      <div className="build-feedback-panel loading">
        <div className="loading-skeleton">
          <div className="vote-summary-skeleton"></div>
          <div className="vote-buttons-skeleton"></div>
          <div className="comments-skeleton"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="build-feedback-panel">
      {/* Vote Summary */}
      {showVoteSummary && voteSummary && (
        <div className="vote-summary-section">
          <h3>Community Feedback</h3>
          <div className="vote-summary">
            <div className="vote-stats">
              <div className="vote-score">
                <span className="score-value" style={{ color: voteSummary.score > 0 ? '#4ade80' : voteSummary.score < 0 ? '#f87171' : '#a0a0a0' }}>
                  {voteSummary.score > 0 ? '+' : ''}{voteSummary.score}
                </span>
                <span className="score-label">Score</span>
              </div>
              <div className="vote-breakdown">
                <span className="vote-count">👍 {voteSummary.thumbs_up}</span>
                <span className="vote-count">👎 {voteSummary.thumbs_down}</span>
                {voteSummary.neutral > 0 && <span className="vote-count">➖ {voteSummary.neutral}</span>}
              </div>
            </div>
            <div className="vote-total">
              <span>{voteSummary.total_votes} total votes</span>
              {voteSummary.popularity_rank > 0 && (
                <span className="popularity-rank">Rank #{voteSummary.popularity_rank}</span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Vote Buttons */}
      <div className="vote-section">
        <h4>Rate this {contentType}</h4>
        <div className="vote-buttons">
          <button
            className={`vote-btn thumbs-up ${userVote?.vote_type === 'thumbs_up' ? 'active' : ''}`}
            onClick={() => handleVoteClick('thumbs_up')}
            disabled={submitting}
          >
            <span className="vote-icon">👍</span>
            <span className="vote-label">Thumbs Up</span>
          </button>

          <button
            className={`vote-btn neutral ${userVote?.vote_type === 'neutral' ? 'active' : ''}`}
            onClick={() => handleVoteClick('neutral')}
            disabled={submitting}
          >
            <span className="vote-icon">➖</span>
            <span className="vote-label">Neutral</span>
          </button>

          <button
            className={`vote-btn thumbs-down ${userVote?.vote_type === 'thumbs_down' ? 'active' : ''}`}
            onClick={() => handleVoteClick('thumbs_down')}
            disabled={submitting}
          >
            <span className="vote-icon">👎</span>
            <span className="vote-label">Thumbs Down</span>
          </button>
        </div>
      </div>

      {/* Comments Section */}
      {showComments && (
        <div className="comments-section">
          <h4>Comments & Feedback</h4>
          
          {/* Add Comment */}
          <div className="add-comment">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Share your thoughts about this content..."
              rows={3}
              disabled={submitting}
            />
            <div className="comment-actions">
              <button
                className="btn btn-primary"
                onClick={submitComment}
                disabled={!newComment.trim() || submitting}
              >
                {submitting ? 'Posting...' : 'Post Comment'}
              </button>
            </div>
          </div>

          {/* Comments List */}
          <div className="comments-list">
            {comments.length === 0 ? (
              <div className="no-comments">
                <span className="no-comments-icon">💬</span>
                <p>No comments yet. Be the first to share your thoughts!</p>
              </div>
            ) : (
              comments.map(comment => (
                <div key={comment.id} className="comment">
                  <div className="comment-header">
                    <span className="comment-author">
                      {comment.author}
                      {comment.is_creator_reply && (
                        <span className="creator-badge">Creator</span>
                      )}
                    </span>
                    <span className="comment-date">{formatDate(comment.created_at)}</span>
                  </div>
                  <div className="comment-content">{comment.content}</div>
                  
                  {/* Reply Button */}
                  <div className="comment-actions">
                    <button
                      className="reply-btn"
                      onClick={() => setReplyingTo(comment.id)}
                    >
                      Reply
                    </button>
                  </div>

                  {/* Reply Form */}
                  {replyingTo === comment.id && (
                    <div className="reply-form">
                      <textarea
                        value={replyContent}
                        onChange={(e) => setReplyContent(e.target.value)}
                        placeholder="Write a reply..."
                        rows={2}
                      />
                      <div className="reply-actions">
                        <button
                          className="btn btn-secondary"
                          onClick={() => {
                            setReplyingTo(null);
                            setReplyContent('');
                          }}
                        >
                          Cancel
                        </button>
                        <button
                          className="btn btn-primary"
                          onClick={() => {
                            // Handle reply submission
                            setReplyingTo(null);
                            setReplyContent('');
                          }}
                          disabled={!replyContent.trim()}
                        >
                          Reply
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Replies */}
                  {comment.replies.length > 0 && (
                    <div className="replies">
                      {comment.replies.map(reply => (
                        <div key={reply.id} className="reply">
                          <div className="reply-header">
                            <span className="reply-author">
                              {reply.author}
                              {reply.is_creator_reply && (
                                <span className="creator-badge">Creator</span>
                              )}
                            </span>
                            <span className="reply-date">{formatDate(reply.created_at)}</span>
                          </div>
                          <div className="reply-content">{reply.content}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Vote Modal */}
      {showVoteModal && (
        <div className="vote-modal" onClick={() => setShowVoteModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Vote on "{contentTitle}"</h3>
              <button className="close-btn" onClick={() => setShowVoteModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="vote-type-display">
                <span className="vote-icon-large">{getVoteIcon(pendingVoteType || '')}</span>
                <span className="vote-type-label">
                  {pendingVoteType === 'thumbs_up' ? 'Thumbs Up' :
                   pendingVoteType === 'thumbs_down' ? 'Thumbs Down' : 'Neutral'}
                </span>
              </div>
              
              <div className="form-group">
                <label htmlFor="vote-reason">Reason for your vote (optional):</label>
                <textarea
                  id="vote-reason"
                  value={voteForm.reason}
                  onChange={(e) => setVoteForm(prev => ({ ...prev, reason: e.target.value }))}
                  placeholder="Why did you vote this way?"
                  rows={3}
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="vote-feedback">Additional feedback (optional):</label>
                <textarea
                  id="vote-feedback"
                  value={voteForm.feedback}
                  onChange={(e) => setVoteForm(prev => ({ ...prev, feedback: e.target.value }))}
                  placeholder="Any suggestions for improvement?"
                  rows={3}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={() => setShowVoteModal(false)}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={submitVote}
                disabled={submitting}
              >
                {submitting ? 'Submitting...' : 'Submit Vote'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      {error && (
        <div className="error-message" onClick={clearMessages}>
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
          <button className="dismiss-btn">×</button>
        </div>
      )}

      {successMessage && (
        <div className="success-message" onClick={clearMessages}>
          <span className="success-icon">✅</span>
          <span>{successMessage}</span>
          <button className="dismiss-btn">×</button>
        </div>
      )}
    </div>
  );
};

export default BuildFeedbackPanel; 