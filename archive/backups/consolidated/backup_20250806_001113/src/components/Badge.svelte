<script>
  export let type = 'guide-author'; // guide-author, modder, bug-hunter, tester, community-helper
  export let size = 'medium'; // small, medium, large
  export let animated = false;
  export let clickable = false;
  
  let hovered = false;
  
  const badgeConfig = {
    'guide-author': {
      label: 'Guide Author',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      icon: '📚',
      description: 'Created comprehensive guides and documentation'
    },
    'modder': {
      label: 'Modder',
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      icon: '🔧',
      description: 'Developed mods and tools for the community'
    },
    'bug-hunter': {
      label: 'Bug Hunter',
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      icon: '🐛',
      description: 'Found and reported critical bugs and issues'
    },
    'tester': {
      label: 'Tester',
      gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
      icon: '🧪',
      description: 'Provided extensive testing and feedback'
    },
    'community-helper': {
      label: 'Community Helper',
      gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      icon: '🤝',
      description: 'Helped support and grow the community'
    }
  };
  
  const sizeConfig = {
    small: {
      padding: '0.25rem 0.5rem',
      fontSize: '0.7rem',
      iconSize: '0.8rem'
    },
    medium: {
      padding: '0.25rem 0.75rem',
      fontSize: '0.8rem',
      iconSize: '1rem'
    },
    large: {
      padding: '0.5rem 1rem',
      fontSize: '1rem',
      iconSize: '1.2rem'
    }
  };
  
  $: config = badgeConfig[type] || badgeConfig['guide-author'];
  $: sizeStyle = sizeConfig[size] || sizeConfig.medium;
  
  function handleClick() {
    if (clickable) {
      // Dispatch custom event for badge click
      dispatchEvent(new CustomEvent('badgeClick', {
        detail: { type, label: config.label }
      }));
    }
  }
  
  function handleMouseEnter() {
    if (animated) {
      hovered = true;
    }
  }
  
  function handleMouseLeave() {
    if (animated) {
      hovered = false;
    }
  }
</script>

<span
  class="badge {type} {size} {clickable ? 'clickable' : ''} {animated ? 'animated' : ''} {hovered ? 'hovered' : ''}"
  style="
    padding: {sizeStyle.padding};
    font-size: {sizeStyle.fontSize};
    background: {config.gradient};
  "
  on:click={handleClick}
  on:mouseenter={handleMouseEnter}
  on:mouseleave={handleMouseLeave}
  role="button"
  tabindex={clickable ? 0 : undefined}
  title={config.description}
>
  <span class="badge-icon" style="font-size: {sizeStyle.iconSize};">{config.icon}</span>
  <span class="badge-label">{config.label}</span>
</span>

<style>
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    border-radius: 20px;
    font-weight: 500;
    color: white;
    text-decoration: none;
    border: none;
    cursor: default;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    user-select: none;
  }
  
  .badge.clickable {
    cursor: pointer;
  }
  
  .badge.clickable:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  }
  
  .badge.animated {
    transition: all 0.3s ease;
  }
  
  .badge.animated.hovered {
    transform: scale(1.05);
    box-shadow: 0 6px 12px rgba(0,0,0,0.2);
  }
  
  .badge-icon {
    display: inline-block;
  }
  
  .badge-label {
    font-weight: 600;
    letter-spacing: 0.5px;
  }
  
  /* Focus styles for accessibility */
  .badge.clickable:focus {
    outline: 2px solid #3498db;
    outline-offset: 2px;
  }
  
  /* Specific badge type styles */
  .badge.guide-author {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .badge.modder {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  }
  
  .badge.bug-hunter {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  }
  
  .badge.tester {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  }
  
  .badge.community-helper {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  }
  
  /* Size variations */
  .badge.small {
    padding: 0.25rem 0.5rem;
    font-size: 0.7rem;
  }
  
  .badge.small .badge-icon {
    font-size: 0.8rem;
  }
  
  .badge.medium {
    padding: 0.25rem 0.75rem;
    font-size: 0.8rem;
  }
  
  .badge.medium .badge-icon {
    font-size: 1rem;
  }
  
  .badge.large {
    padding: 0.5rem 1rem;
    font-size: 1rem;
  }
  
  .badge.large .badge-icon {
    font-size: 1.2rem;
  }
  
  /* Animation keyframes */
  @keyframes badgePulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
  }
  
  .badge.animated:hover {
    animation: badgePulse 0.6s ease-in-out;
  }
  
  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .badge {
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .badge.clickable:hover {
      box-shadow: 0 4px 8px rgba(0,0,0,0.4);
    }
  }
  
  /* Mobile responsiveness */
  @media (max-width: 768px) {
    .badge {
      font-size: 0.75rem;
    }
    
    .badge-icon {
      font-size: 0.9rem;
    }
  }
</style> 