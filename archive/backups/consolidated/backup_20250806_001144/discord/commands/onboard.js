const { SlashCommandBuilder, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
const { spawn } = require('child_process');
const path = require('path');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('onboard')
        .setDescription('Run the MS11 onboarding wizard')
        .addStringOption(option =>
            option.setName('user_hash')
                .setDescription('Your unique user identifier (optional)')
                .setRequired(false)),

    async execute(interaction) {
        const userHash = interaction.options.getString('user_hash') || `discord_${interaction.user.id}`;
        
        // Create initial embed
        const embed = new EmbedBuilder()
            .setColor('#0099ff')
            .setTitle('🎯 MS11 Onboarding Wizard')
            .setDescription('Starting the onboarding process...')
            .addFields(
                { name: 'User', value: interaction.user.username, inline: true },
                { name: 'User Hash', value: userHash, inline: true },
                { name: 'Status', value: '🔄 Initializing...', inline: true }
            )
            .setTimestamp()
            .setFooter({ text: 'MS11 Onboarding System' });

        const row = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('onboard_start')
                    .setLabel('Start Onboarding')
                    .setStyle(ButtonStyle.Primary)
                    .setEmoji('🚀'),
                new ButtonBuilder()
                    .setCustomId('onboard_status')
                    .setLabel('Check Status')
                    .setStyle(ButtonStyle.Secondary)
                    .setEmoji('📊'),
                new ButtonBuilder()
                    .setCustomId('onboard_help')
                    .setLabel('Help')
                    .setStyle(ButtonStyle.Secondary)
                    .setEmoji('❓')
            );

        const response = await interaction.reply({
            embeds: [embed],
            components: [row],
            fetchReply: true
        });

        // Start the onboarding process
        await startOnboarding(interaction, userHash, response);
    }
};

async function startOnboarding(interaction, userHash, response) {
    try {
        // Update embed to show progress
        const progressEmbed = new EmbedBuilder()
            .setColor('#ffaa00')
            .setTitle('🎯 MS11 Onboarding Wizard')
            .setDescription('Running onboarding checks...')
            .addFields(
                { name: 'User', value: interaction.user.username, inline: true },
                { name: 'User Hash', value: userHash, inline: true },
                { name: 'Status', value: '🔄 Running checks...', inline: true }
            )
            .setTimestamp()
            .setFooter({ text: 'MS11 Onboarding System' });

        await response.edit({ embeds: [progressEmbed] });

        // Run the Python onboarding wizard
        const onboardingResult = await runOnboardingWizard(userHash);
        
        // Create result embed
        const resultEmbed = new EmbedBuilder()
            .setColor(onboardingResult.success ? '#00ff00' : '#ff0000')
            .setTitle('🎯 MS11 Onboarding Complete')
            .setDescription(onboardingResult.success ? 
                '✅ Onboarding completed successfully!' : 
                '❌ Onboarding completed with issues.')
            .addFields(
                { name: 'User', value: interaction.user.username, inline: true },
                { name: 'User Hash', value: userHash, inline: true },
                { name: 'Steps Completed', value: `${onboardingResult.stepsCompleted}/${onboardingResult.totalSteps}`, inline: true },
                { name: 'Setup Time', value: `${onboardingResult.setupTime.toFixed(2)}s`, inline: true }
            )
            .setTimestamp()
            .setFooter({ text: 'MS11 Onboarding System' });

        if (onboardingResult.failedSteps.length > 0) {
            resultEmbed.addFields({
                name: '❌ Failed Steps',
                value: onboardingResult.failedSteps.join(', '),
                inline: false
            });
        }

        if (onboardingResult.recommendations.length > 0) {
            resultEmbed.addFields({
                name: '💡 Recommendations',
                value: onboardingResult.recommendations.slice(0, 3).join('\n'),
                inline: false
            });
        }

        // Add tutorial link
        if (onboardingResult.tutorialUrl) {
            resultEmbed.addFields({
                name: '📹 Tutorial Video',
                value: onboardingResult.tutorialUrl,
                inline: false
            });
        }

        // Update response with results
        const resultRow = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('onboard_validate')
                    .setLabel('Run Validation')
                    .setStyle(ButtonStyle.Primary)
                    .setEmoji('🔍'),
                new ButtonBuilder()
                    .setCustomId('onboard_status')
                    .setLabel('Check Status')
                    .setStyle(ButtonStyle.Secondary)
                    .setEmoji('📊'),
                new ButtonBuilder()
                    .setCustomId('onboard_help')
                    .setLabel('Help')
                    .setStyle(ButtonStyle.Secondary)
                    .setEmoji('❓')
            );

        await response.edit({
            embeds: [resultEmbed],
            components: [resultRow]
        });

    } catch (error) {
        console.error('Onboarding error:', error);
        
        const errorEmbed = new EmbedBuilder()
            .setColor('#ff0000')
            .setTitle('❌ Onboarding Error')
            .setDescription('An error occurred during onboarding.')
            .addFields(
                { name: 'Error', value: error.message, inline: false },
                { name: 'User', value: interaction.user.username, inline: true },
                { name: 'User Hash', value: userHash, inline: true }
            )
            .setTimestamp()
            .setFooter({ text: 'MS11 Onboarding System' });

        await response.edit({
            embeds: [errorEmbed],
            components: []
        });
    }
}

async function runOnboardingWizard(userHash) {
    return new Promise((resolve, reject) => {
        const projectRoot = path.resolve(__dirname, '../../..');
        const pythonScript = path.join(projectRoot, 'onboarding', 'wizard.py');
        
        const child = spawn('python', [pythonScript, '--user-hash', userHash], {
            cwd: projectRoot,
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let output = '';
        let errorOutput = '';

        child.stdout.on('data', (data) => {
            output += data.toString();
        });

        child.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });

        child.on('close', (code) => {
            if (code === 0) {
                try {
                    // Parse the output to extract onboarding results
                    const result = parseOnboardingOutput(output);
                    resolve(result);
                } catch (error) {
                    reject(new Error(`Failed to parse onboarding output: ${error.message}`));
                }
            } else {
                reject(new Error(`Onboarding failed with code ${code}: ${errorOutput}`));
            }
        });

        child.on('error', (error) => {
            reject(new Error(`Failed to start onboarding process: ${error.message}`));
        });
    });
}

function parseOnboardingOutput(output) {
    // Parse the Python script output to extract results
    const lines = output.split('\n');
    
    let stepsCompleted = 0;
    let totalSteps = 0;
    let failedSteps = [];
    let recommendations = [];
    let setupTime = 0;
    let tutorialUrl = '';
    let success = true;

    for (const line of lines) {
        if (line.includes('Steps completed:')) {
            const match = line.match(/(\d+)\/(\d+)/);
            if (match) {
                stepsCompleted = parseInt(match[1]);
                totalSteps = parseInt(match[2]);
            }
        } else if (line.includes('Failed steps:')) {
            const failedMatch = line.match(/Failed steps: (.+)/);
            if (failedMatch) {
                failedSteps = failedMatch[1].split(', ').filter(s => s.trim());
                success = failedSteps.length === 0;
            }
        } else if (line.includes('Recommendations:')) {
            const recMatch = line.match(/Recommendations: (\d+)/);
            if (recMatch) {
                const recCount = parseInt(recMatch[1]);
                // Extract recommendations from subsequent lines
                recommendations = lines
                    .slice(lines.indexOf(line) + 1)
                    .filter(l => l.trim().startsWith('-') || l.trim().startsWith('•'))
                    .slice(0, recCount)
                    .map(l => l.trim().replace(/^[-•]\s*/, ''));
            }
        } else if (line.includes('completed in')) {
            const timeMatch = line.match(/(\d+\.\d+) seconds/);
            if (timeMatch) {
                setupTime = parseFloat(timeMatch[1]);
            }
        } else if (line.includes('Tutorial video:')) {
            const urlMatch = line.match(/Tutorial video: (.+)/);
            if (urlMatch) {
                tutorialUrl = urlMatch[1];
            }
        }
    }

    return {
        success,
        stepsCompleted,
        totalSteps,
        failedSteps,
        recommendations,
        setupTime,
        tutorialUrl
    };
}

// Handle button interactions
module.exports.handleButtonInteraction = async (interaction) => {
    const { customId } = interaction;

    switch (customId) {
        case 'onboard_start':
            await interaction.reply({ content: '🚀 Starting onboarding process...', ephemeral: true });
            break;
            
        case 'onboard_status':
            await showOnboardingStatus(interaction);
            break;
            
        case 'onboard_validate':
            await runValidation(interaction);
            break;
            
        case 'onboard_help':
            await showOnboardingHelp(interaction);
            break;
            
        default:
            await interaction.reply({ content: 'Unknown button interaction', ephemeral: true });
    }
};

async function showOnboardingStatus(interaction) {
    const userHash = `discord_${interaction.user.id}`;
    
    try {
        const status = await getOnboardingStatus(userHash);
        
        if (status) {
            const statusEmbed = new EmbedBuilder()
                .setColor('#0099ff')
                .setTitle('📊 Onboarding Status')
                .setDescription(`Status for user: ${interaction.user.username}`)
                .addFields(
                    { name: 'User Hash', value: userHash, inline: true },
                    { name: 'Steps Completed', value: `${status.steps_completed}/${status.total_steps}`, inline: true },
                    { name: 'Setup Time', value: `${status.setup_time.toFixed(2)}s`, inline: true }
                )
                .setTimestamp();

            if (status.failed_steps && status.failed_steps.length > 0) {
                statusEmbed.addFields({
                    name: '❌ Failed Steps',
                    value: status.failed_steps.join(', '),
                    inline: false
                });
            }

            await interaction.reply({ embeds: [statusEmbed], ephemeral: true });
        } else {
            await interaction.reply({ 
                content: '❌ No onboarding data found. Run `/onboard` first.', 
                ephemeral: true 
            });
        }
    } catch (error) {
        await interaction.reply({ 
            content: `❌ Error checking status: ${error.message}`, 
            ephemeral: true 
        });
    }
}

async function runValidation(interaction) {
    await interaction.reply({ 
        content: '🔍 Running validation checks... Use `/validate` for detailed validation.', 
        ephemeral: true 
    });
}

async function showOnboardingHelp(interaction) {
    const helpEmbed = new EmbedBuilder()
        .setColor('#0099ff')
        .setTitle('❓ Onboarding Help')
        .setDescription('MS11 Onboarding Wizard Guide')
        .addFields(
            { name: '🎯 What is Onboarding?', value: 'Onboarding sets up MS11 for first-time use, checking system compatibility and creating necessary configurations.', inline: false },
            { name: '📋 Steps', value: '1. System Check\n2. Game Detection\n3. Configuration Setup\n4. Discord Setup\n5. Validation\n6. Tutorial Setup', inline: false },
            { name: '💡 Tips', value: '• Ensure SWG is running\n• Have Discord bot token ready\n• Check system requirements\n• Review generated checklist', inline: false },
            { name: '🔧 Commands', value: '`/onboard` - Run wizard\n`/validate` - Run checks\n`/status` - Check status', inline: false }
        )
        .setTimestamp()
        .setFooter({ text: 'MS11 Help System' });

    await interaction.reply({ embeds: [helpEmbed], ephemeral: true });
}

async function getOnboardingStatus(userHash) {
    // This would typically call a Python function to get status
    // For now, return a mock status
    return {
        user_hash: userHash,
        steps_completed: 6,
        total_steps: 8,
        setup_time: 45.2,
        failed_steps: [],
        recommendations: []
    };
} 