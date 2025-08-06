<script>
  import { onMount, createEventDispatcher } from 'svelte';
  
  // Props
  export let mapData = null;
  export let coordinates = [0, 0];
  export let showGrid = true;
  export let showLabels = true;
  export let showPaths = true;
  export let interactiveMode = true;
  export let selectedZone = null;
  export let selectedMarker = null;
  
  // Component state
  let mapContainer;
  let canvas;
  let ctx;
  let mapScale = 1;
  let mapOffset = { x: 0, y: 0 };
  let isDragging = false;
  let dragStart = { x: 0, y: 0 };
  let hoveredElement = null;
  let tooltip = { visible: false, x: 0, y: 0, content: '' };
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Map configuration
  const config = {
    gridColor: '#e0e0e0',
    gridSize: 50,
    zoneColors: {
      entrance: '#4CAF50',
      corridor: '#2196F3', 
      encounter: '#FF9800',
      boss: '#F44336',
      area: '#9C27B0',
      secret: '#795548'
    },
    markerIcons: {
      spawn: '🚪',
      checkpoint: '🏁',
      loot: '📦',
      boss_chest: '💎',
      portal: '🌀',
      altar: '⚡',
      crystal: '💠',
      chest: '📦'
    },
    pathColors: {
      normal: '#4CAF50',
      hard: '#F44336',
      secret: '#9C27B0'
    }
  };
  
  onMount(() => {
    if (mapContainer && mapData) {
      initializeMap();
      renderMap();
      
      // Add event listeners
      canvas.addEventListener('mousedown', handleMouseDown);
      canvas.addEventListener('mousemove', handleMouseMove);
      canvas.addEventListener('mouseup', handleMouseUp);
      canvas.addEventListener('wheel', handleWheel);
      canvas.addEventListener('mouseleave', handleMouseLeave);
      
      // Resize observer
      const resizeObserver = new ResizeObserver(() => {
        resizeCanvas();
        renderMap();
      });
      resizeObserver.observe(mapContainer);
      
      return () => {
        resizeObserver.disconnect();
      };
    }
  });
  
  function initializeMap() {
    canvas = mapContainer.querySelector('canvas');
    ctx = canvas.getContext('2d');
    resizeCanvas();
    
    // Center map on main coordinates
    if (coordinates && mapData.mapData?.bounds) {
      const bounds = mapData.mapData.bounds;
      const centerX = (bounds.east + bounds.west) / 2;
      const centerY = (bounds.north + bounds.south) / 2;
      
      mapOffset.x = canvas.width / 2 - centerX;
      mapOffset.y = canvas.height / 2 - centerY;
    }
  }
  
  function resizeCanvas() {
    const rect = mapContainer.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
  }
  
  function renderMap() {
    if (!ctx || !mapData) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Save context state
    ctx.save();
    
    // Apply transformations
    ctx.scale(mapScale, mapScale);
    ctx.translate(mapOffset.x, mapOffset.y);
    
    // Render grid
    if (showGrid) {
      renderGrid();
    }
    
    // Render paths
    if (showPaths && mapData.paths) {
      renderPaths();
    }
    
    // Render zones
    if (mapData.zones) {
      renderZones();
    }
    
    // Render markers
    if (mapData.markers) {
      renderMarkers();
    }
    
    // Render hazards
    if (mapData.hazards) {
      renderHazards();
    }
    
    // Render secrets
    if (mapData.secrets) {
      renderSecrets();
    }
    
    // Restore context state
    ctx.restore();
  }
  
  function renderGrid() {
    const bounds = mapData.mapData?.bounds;
    if (!bounds) return;
    
    ctx.strokeStyle = config.gridColor;
    ctx.lineWidth = 1;
    ctx.setLineDash([]);
    
    const gridSize = config.gridSize;
    
    // Vertical lines
    for (let x = bounds.west; x <= bounds.east; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, bounds.north);
      ctx.lineTo(x, bounds.south);
      ctx.stroke();
    }
    
    // Horizontal lines
    for (let y = bounds.north; y >= bounds.south; y -= gridSize) {
      ctx.beginPath();
      ctx.moveTo(bounds.west, y);
      ctx.lineTo(bounds.east, y);
      ctx.stroke();
    }
  }
  
  function renderPaths() {
    mapData.paths.forEach(path => {
      const color = config.pathColors[path.difficulty] || config.pathColors.normal;
      
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.setLineDash([10, 5]);
      ctx.globalAlpha = 0.7;
      
      ctx.beginPath();
      path.waypoints.forEach((waypoint, index) => {
        const [x, y] = waypoint;
        if (index === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      ctx.stroke();
      
      ctx.globalAlpha = 1;
      ctx.setLineDash([]);
    });
  }
  
  function renderZones() {
    mapData.zones.forEach(zone => {
      const [x, y] = zone.coordinates;
      const color = config.zoneColors[zone.type] || '#888';
      const isSelected = selectedZone === zone.id;
      const isHovered = hoveredElement?.type === 'zone' && hoveredElement?.id === zone.id;
      
      // Zone circle
      ctx.fillStyle = color;
      ctx.globalAlpha = isSelected ? 0.8 : (isHovered ? 0.6 : 0.4);
      
      ctx.beginPath();
      ctx.arc(x, y, 30, 0, Math.PI * 2);
      ctx.fill();
      
      // Zone border
      ctx.strokeStyle = color;
      ctx.lineWidth = isSelected ? 3 : 2;
      ctx.globalAlpha = 1;
      ctx.stroke();
      
      // Zone label
      if (showLabels) {
        ctx.fillStyle = '#000';
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(zone.name, x, y + 45);
      }
    });
  }
  
  function renderMarkers() {
    mapData.markers.forEach(marker => {
      const [x, y] = marker.coordinates;
      const icon = config.markerIcons[marker.type] || '📍';
      const isSelected = selectedMarker === marker.id;
      const isHovered = hoveredElement?.type === 'marker' && hoveredElement?.id === marker.id;
      
      // Marker background
      if (isSelected || isHovered) {
        ctx.fillStyle = isSelected ? '#FFD700' : '#FFF';
        ctx.beginPath();
        ctx.arc(x, y, 15, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.stroke();
      }
      
      // Marker icon
      ctx.font = '20px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(icon, x, y);
      
      // Marker label
      if (showLabels) {
        ctx.fillStyle = '#000';
        ctx.font = '10px Arial';
        ctx.fillText(marker.name, x, y + 25);
      }
    });
  }
  
  function renderHazards() {
    mapData.hazards.forEach(hazard => {
      const [x, y] = hazard.coordinates;
      
      // Hazard warning area
      ctx.fillStyle = '#FF5722';
      ctx.globalAlpha = 0.3;
      
      ctx.beginPath();
      ctx.arc(x, y, 25, 0, Math.PI * 2);
      ctx.fill();
      
      // Hazard icon
      ctx.globalAlpha = 1;
      ctx.font = '16px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('⚠️', x, y);
    });
  }
  
  function renderSecrets() {
    mapData.secrets.forEach(secret => {
      const [x, y] = secret.coordinates;
      
      // Secret area (dashed circle)
      ctx.strokeStyle = config.zoneColors.secret;
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.globalAlpha = 0.8;
      
      ctx.beginPath();
      ctx.arc(x, y, 20, 0, Math.PI * 2);
      ctx.stroke();
      
      // Secret icon
      ctx.globalAlpha = 1;
      ctx.setLineDash([]);
      ctx.font = '16px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('🔍', x, y);
    });
  }
  
  function worldToScreen(worldX, worldY) {
    return {
      x: (worldX + mapOffset.x) * mapScale,
      y: (worldY + mapOffset.y) * mapScale
    };
  }
  
  function screenToWorld(screenX, screenY) {
    return {
      x: screenX / mapScale - mapOffset.x,
      y: screenY / mapScale - mapOffset.y
    };
  }
  
  function getElementAtPosition(x, y) {
    const worldPos = screenToWorld(x, y);
    
    // Check markers first (smallest targets)
    for (const marker of mapData.markers || []) {
      const [mx, my] = marker.coordinates;
      const distance = Math.sqrt((worldPos.x - mx) ** 2 + (worldPos.y - my) ** 2);
      if (distance <= 15) {
        return { type: 'marker', id: marker.id, data: marker };
      }
    }
    
    // Check zones
    for (const zone of mapData.zones || []) {
      const [zx, zy] = zone.coordinates;
      const distance = Math.sqrt((worldPos.x - zx) ** 2 + (worldPos.y - zy) ** 2);
      if (distance <= 30) {
        return { type: 'zone', id: zone.id, data: zone };
      }
    }
    
    // Check hazards
    for (const hazard of mapData.hazards || []) {
      const [hx, hy] = hazard.coordinates;
      const distance = Math.sqrt((worldPos.x - hx) ** 2 + (worldPos.y - hy) ** 2);
      if (distance <= 25) {
        return { type: 'hazard', id: hazard.id, data: hazard };
      }
    }
    
    // Check secrets
    for (const secret of mapData.secrets || []) {
      const [sx, sy] = secret.coordinates;
      const distance = Math.sqrt((worldPos.x - sx) ** 2 + (worldPos.y - sy) ** 2);
      if (distance <= 20) {
        return { type: 'secret', id: secret.id, data: secret };
      }
    }
    
    return null;
  }
  
  function handleMouseDown(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    const element = getElementAtPosition(x, y);
    
    if (element && interactiveMode) {
      // Select element
      if (element.type === 'zone') {
        selectedZone = element.id;
        dispatch('zoneSelected', element.data);
      } else if (element.type === 'marker') {
        selectedMarker = element.id;
        dispatch('markerSelected', element.data);
      }
      
      renderMap();
    } else {
      // Start dragging
      isDragging = true;
      dragStart = { x, y };
    }
  }
  
  function handleMouseMove(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    if (isDragging) {
      // Pan the map
      const deltaX = x - dragStart.x;
      const deltaY = y - dragStart.y;
      
      mapOffset.x += deltaX / mapScale;
      mapOffset.y += deltaY / mapScale;
      
      dragStart = { x, y };
      renderMap();
    } else {
      // Handle hover
      const element = getElementAtPosition(x, y);
      
      if (element !== hoveredElement) {
        hoveredElement = element;
        
        if (element) {
          // Show tooltip
          tooltip = {
            visible: true,
            x: event.clientX,
            y: event.clientY,
            content: `${element.data.name}: ${element.data.description || 'No description'}`
          };
          canvas.style.cursor = 'pointer';
        } else {
          tooltip.visible = false;
          canvas.style.cursor = isDragging ? 'grabbing' : 'grab';
        }
        
        renderMap();
      }
    }
  }
  
  function handleMouseUp() {
    isDragging = false;
    canvas.style.cursor = 'grab';
  }
  
  function handleMouseLeave() {
    isDragging = false;
    hoveredElement = null;
    tooltip.visible = false;
    canvas.style.cursor = 'default';
    renderMap();
  }
  
  function handleWheel(event) {
    event.preventDefault();
    
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    const worldPos = screenToWorld(x, y);
    const scaleFactor = event.deltaY < 0 ? 1.1 : 0.9;
    const newScale = Math.max(0.5, Math.min(3, mapScale * scaleFactor));
    
    if (newScale !== mapScale) {
      mapScale = newScale;
      
      // Adjust offset to zoom towards mouse position
      const newWorldPos = screenToWorld(x, y);
      mapOffset.x += newWorldPos.x - worldPos.x;
      mapOffset.y += newWorldPos.y - worldPos.y;
      
      renderMap();
    }
  }
  
  // Public methods
  export function centerOnCoordinates(coords) {
    const [x, y] = coords;
    mapOffset.x = canvas.width / 2 / mapScale - x;
    mapOffset.y = canvas.height / 2 / mapScale - y;
    renderMap();
  }
  
  export function resetView() {
    mapScale = 1;
    if (coordinates && mapData.mapData?.bounds) {
      const bounds = mapData.mapData.bounds;
      const centerX = (bounds.east + bounds.west) / 2;
      const centerY = (bounds.north + bounds.south) / 2;
      
      mapOffset.x = canvas.width / 2 - centerX;
      mapOffset.y = canvas.height / 2 - centerY;
    }
    renderMap();
  }
  
  export function toggleLayer(layer) {
    switch(layer) {
      case 'grid':
        showGrid = !showGrid;
        break;
      case 'labels':
        showLabels = !showLabels;
        break;
      case 'paths':
        showPaths = !showPaths;
        break;
    }
    renderMap();
  }
  
  // Reactive updates
  $: if (mapData && canvas) {
    renderMap();
  }
</script>

<div class="map-viewer" bind:this={mapContainer}>
  <canvas></canvas>
  
  <!-- Map Controls -->
  <div class="map-controls">
    <div class="control-group">
      <button class="control-btn" on:click={resetView} title="Reset View">
        🏠
      </button>
      <button class="control-btn" on:click={() => toggleLayer('grid')} 
              class:active={showGrid} title="Toggle Grid">
        ⊞
      </button>
      <button class="control-btn" on:click={() => toggleLayer('labels')} 
              class:active={showLabels} title="Toggle Labels">
        🏷️
      </button>
      <button class="control-btn" on:click={() => toggleLayer('paths')} 
              class:active={showPaths} title="Toggle Paths">
        🛤️
      </button>
    </div>
    
    <!-- Zoom Controls -->
    <div class="zoom-controls">
      <button class="control-btn" on:click={() => handleWheel({deltaY: -100, preventDefault: () => {}})} title="Zoom In">
        ➕
      </button>
      <span class="zoom-level">{Math.round(mapScale * 100)}%</span>
      <button class="control-btn" on:click={() => handleWheel({deltaY: 100, preventDefault: () => {}})} title="Zoom Out">
        ➖
      </button>
    </div>
  </div>
  
  <!-- Legend -->
  <div class="map-legend">
    <h4>Legend</h4>
    <div class="legend-items">
      <div class="legend-item">
        <span class="legend-color" style="background-color: {config.zoneColors.entrance}"></span>
        <span>Entrance</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: {config.zoneColors.encounter}"></span>
        <span>Encounter</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: {config.zoneColors.boss}"></span>
        <span>Boss</span>
      </div>
      <div class="legend-item">
        <span class="legend-icon">{config.markerIcons.loot}</span>
        <span>Loot</span>
      </div>
      <div class="legend-item">
        <span class="legend-icon">{config.markerIcons.checkpoint}</span>
        <span>Checkpoint</span>
      </div>
      <div class="legend-item">
        <span class="legend-icon">⚠️</span>
        <span>Hazard</span>
      </div>
    </div>
  </div>
  
  <!-- Tooltip -->
  {#if tooltip.visible}
    <div class="tooltip" style="left: {tooltip.x + 10}px; top: {tooltip.y - 10}px;">
      {tooltip.content}
    </div>
  {/if}
</div>

<style>
  .map-viewer {
    position: relative;
    width: 100%;
    height: 400px;
    background-color: #f5f5f5;
    border: 2px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
  }
  
  canvas {
    display: block;
    width: 100%;
    height: 100%;
    cursor: grab;
  }
  
  canvas:active {
    cursor: grabbing;
  }
  
  .map-controls {
    position: absolute;
    top: 10px;
    right: 10px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .control-group, .zoom-controls {
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 5px;
    padding: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  }
  
  .zoom-controls {
    align-items: center;
  }
  
  .control-btn {
    background: white;
    border: 1px solid #ddd;
    padding: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 14px;
  }
  
  .control-btn:hover {
    background: #f0f0f0;
    transform: scale(1.05);
  }
  
  .control-btn.active {
    background: #3498db;
    color: white;
    border-color: #3498db;
  }
  
  .zoom-level {
    font-size: 12px;
    font-weight: bold;
    padding: 2px 0;
    text-align: center;
    min-width: 40px;
  }
  
  .map-legend {
    position: absolute;
    bottom: 10px;
    left: 10px;
    background: rgba(255, 255, 255, 0.95);
    padding: 10px;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    font-size: 12px;
  }
  
  .map-legend h4 {
    margin: 0 0 8px 0;
    font-size: 14px;
  }
  
  .legend-items {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  
  .legend-color {
    width: 12px;
    height: 12px;
    border-radius: 2px;
    border: 1px solid #333;
  }
  
  .legend-icon {
    font-size: 12px;
    width: 12px;
    text-align: center;
  }
  
  .tooltip {
    position: fixed;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 12px;
    pointer-events: none;
    z-index: 1000;
    max-width: 200px;
    word-wrap: break-word;
  }
  
  @media (max-width: 768px) {
    .map-viewer {
      height: 300px;
    }
    
    .map-controls {
      top: 5px;
      right: 5px;
    }
    
    .map-legend {
      bottom: 5px;
      left: 5px;
      font-size: 10px;
    }
    
    .control-btn {
      padding: 6px;
      font-size: 12px;
    }
  }
</style>