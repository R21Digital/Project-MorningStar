import React, { useState, useEffect, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Alert,
  Pagination,
  CircularProgress
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  Visibility as VisibilityIcon,
  Store as StoreIcon,
  LocationOn as LocationIcon,
  AttachMoney as MoneyIcon,
  Schedule as TimeIcon
} from '@mui/icons-material';

interface DiscoveredItem {
  item_id: string;
  item_name: string;
  category: string;
  cost: number;
  vendor_id: string;
  vendor_name: string;
  vendor_type: string;
  planet: string;
  location: string;
  coordinates: [number, number];
  timestamp: string;
  quality?: string;
  stats?: Record<string, any>;
  resists?: Record<string, any>;
  notes?: string;
}

interface VendorProfile {
  vendor_id: string;
  vendor_name: string;
  vendor_type: string;
  planet: string;
  location: string;
  coordinates: [number, number];
  first_discovered: string;
  last_visited: string;
  total_visits: number;
  items_discovered: number;
  average_item_cost: number;
  most_expensive_item?: string;
  most_expensive_cost: number;
  notes?: string;
}

interface VendorDiscoveryTableProps {
  characterName?: string;
  onItemSelect?: (item: DiscoveredItem) => void;
  onVendorSelect?: (vendor: VendorProfile) => void;
}

const VendorDiscoveryTable: React.FC<VendorDiscoveryTableProps> = ({
  characterName,
  onItemSelect,
  onVendorSelect
}) => {
  const [items, setItems] = useState<DiscoveredItem[]>([]);
  const [vendors, setVendors] = useState<VendorProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filter states
  const [itemNameFilter, setItemNameFilter] = useState('');
  const [vendorTypeFilter, setVendorTypeFilter] = useState('');
  const [planetFilter, setPlanetFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [minCostFilter, setMinCostFilter] = useState('');
  const [maxCostFilter, setMaxCostFilter] = useState('');
  
  // Pagination states
  const [page, setPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  
  // Modal states
  const [selectedItem, setSelectedItem] = useState<DiscoveredItem | null>(null);
  const [selectedVendor, setSelectedVendor] = useState<VendorProfile | null>(null);
  const [itemModalOpen, setItemModalOpen] = useState(false);
  const [vendorModalOpen, setVendorModalOpen] = useState(false);
  
  // Sort states
  const [sortBy, setSortBy] = useState<keyof DiscoveredItem>('timestamp');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Load data on component mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simulate API calls - in real implementation, these would be actual API calls
      const [itemsData, vendorsData] = await Promise.all([
        fetchItemsData(),
        fetchVendorsData()
      ]);
      
      setItems(itemsData);
      setVendors(vendorsData);
    } catch (err) {
      setError('Failed to load data. Please try again.');
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchItemsData = async (): Promise<DiscoveredItem[]> => {
    // Simulate API call
    return [
      {
        item_id: 'item_001',
        item_name: 'Enhanced Composite Chest',
        category: 'armor',
        cost: 75000,
        vendor_id: 'vendor_001',
        vendor_name: 'Corellian Armor Smith',
        vendor_type: 'armorsmith',
        planet: 'Corellia',
        location: 'Coronet City',
        coordinates: [0.0, 0.0],
        timestamp: '2024-01-15T10:30:00',
        quality: 'Exceptional',
        stats: { constitution: 25, stamina: 20 },
        resists: { energy: 30, kinetic: 25 }
      },
      {
        item_id: 'item_002',
        item_name: 'Krayt Dragon Bone Sword',
        category: 'weapons',
        cost: 150000,
        vendor_id: 'vendor_002',
        vendor_name: 'Tatooine Weaponsmith',
        vendor_type: 'weaponsmith',
        planet: 'Tatooine',
        location: 'Mos Eisley',
        coordinates: [0.0, 0.0],
        timestamp: '2024-01-15T11:45:00',
        quality: 'Mastercraft',
        stats: { damage: 150, speed: 2.5 },
        resists: {}
      },
      {
        item_id: 'item_003',
        item_name: 'Stun Resist Enhancement',
        category: 'enhancements',
        cost: 25000,
        vendor_id: 'vendor_003',
        vendor_name: 'Naboo Merchant',
        vendor_type: 'merchant',
        planet: 'Naboo',
        location: 'Theed',
        coordinates: [0.0, 0.0],
        timestamp: '2024-01-15T12:15:00',
        quality: 'Good',
        stats: {},
        resists: { stun: 50 }
      }
    ];
  };

  const fetchVendorsData = async (): Promise<VendorProfile[]> => {
    // Simulate API call
    return [
      {
        vendor_id: 'vendor_001',
        vendor_name: 'Corellian Armor Smith',
        vendor_type: 'armorsmith',
        planet: 'Corellia',
        location: 'Coronet City',
        coordinates: [0.0, 0.0],
        first_discovered: '2024-01-15T10:30:00',
        last_visited: '2024-01-15T14:45:00',
        total_visits: 3,
        items_discovered: 12,
        average_item_cost: 25000,
        most_expensive_item: 'Enhanced Composite Chest',
        most_expensive_cost: 75000
      }
    ];
  };

  // Filter and sort items
  const filteredAndSortedItems = useMemo(() => {
    let filtered = items.filter(item => {
      const matchesName = !itemNameFilter || 
        item.item_name.toLowerCase().includes(itemNameFilter.toLowerCase());
      const matchesVendorType = !vendorTypeFilter || 
        item.vendor_type === vendorTypeFilter;
      const matchesPlanet = !planetFilter || 
        item.planet.toLowerCase() === planetFilter.toLowerCase();
      const matchesCategory = !categoryFilter || 
        item.category === categoryFilter;
      const matchesMinCost = !minCostFilter || 
        item.cost >= parseInt(minCostFilter);
      const matchesMaxCost = !maxCostFilter || 
        item.cost <= parseInt(maxCostFilter);
      
      return matchesName && matchesVendorType && matchesPlanet && 
             matchesCategory && matchesMinCost && matchesMaxCost;
    });

    // Sort items
    filtered.sort((a, b) => {
      const aValue = a[sortBy];
      const bValue = b[sortBy];
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        const comparison = aValue.localeCompare(bValue);
        return sortOrder === 'asc' ? comparison : -comparison;
      } else if (typeof aValue === 'number' && typeof bValue === 'number') {
        const comparison = aValue - bValue;
        return sortOrder === 'asc' ? comparison : -comparison;
      }
      
      return 0;
    });

    return filtered;
  }, [items, itemNameFilter, vendorTypeFilter, planetFilter, categoryFilter, 
      minCostFilter, maxCostFilter, sortBy, sortOrder]);

  // Pagination
  const paginatedItems = useMemo(() => {
    const startIndex = (page - 1) * rowsPerPage;
    return filteredAndSortedItems.slice(startIndex, startIndex + rowsPerPage);
  }, [filteredAndSortedItems, page, rowsPerPage]);

  const handleSort = (column: keyof DiscoveredItem) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };

  const handleItemClick = (item: DiscoveredItem) => {
    setSelectedItem(item);
    setItemModalOpen(true);
    onItemSelect?.(item);
  };

  const handleVendorClick = (vendorId: string) => {
    const vendor = vendors.find(v => v.vendor_id === vendorId);
    if (vendor) {
      setSelectedVendor(vendor);
      setVendorModalOpen(true);
      onVendorSelect?.(vendor);
    }
  };

  const clearFilters = () => {
    setItemNameFilter('');
    setVendorTypeFilter('');
    setPlanetFilter('');
    setCategoryFilter('');
    setMinCostFilter('');
    setMaxCostFilter('');
    setPage(1);
  };

  const formatCost = (cost: number) => {
    return cost.toLocaleString() + ' credits';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString() + ' ' + 
           new Date(dateString).toLocaleTimeString();
  };

  const getVendorTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      armorsmith: 'primary',
      weaponsmith: 'secondary',
      tailor: 'success',
      architect: 'warning',
      doctor: 'info',
      entertainer: 'error',
      merchant: 'default',
      bazaar: 'default'
    };
    return colors[type] || 'default';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Search & Filters
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Item Name"
                value={itemNameFilter}
                onChange={(e) => setItemNameFilter(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
                <InputLabel>Vendor Type</InputLabel>
                <Select
                  value={vendorTypeFilter}
                  onChange={(e) => setVendorTypeFilter(e.target.value)}
                  label="Vendor Type"
                >
                  <MenuItem value="">All Types</MenuItem>
                  <MenuItem value="armorsmith">Armorsmith</MenuItem>
                  <MenuItem value="weaponsmith">Weaponsmith</MenuItem>
                  <MenuItem value="tailor">Tailor</MenuItem>
                  <MenuItem value="architect">Architect</MenuItem>
                  <MenuItem value="doctor">Doctor</MenuItem>
                  <MenuItem value="entertainer">Entertainer</MenuItem>
                  <MenuItem value="merchant">Merchant</MenuItem>
                  <MenuItem value="bazaar">Bazaar</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
                <InputLabel>Planet</InputLabel>
                <Select
                  value={planetFilter}
                  onChange={(e) => setPlanetFilter(e.target.value)}
                  label="Planet"
                >
                  <MenuItem value="">All Planets</MenuItem>
                  <MenuItem value="corellia">Corellia</MenuItem>
                  <MenuItem value="naboo">Naboo</MenuItem>
                  <MenuItem value="tatooine">Tatooine</MenuItem>
                  <MenuItem value="endor">Endor</MenuItem>
                  <MenuItem value="dantooine">Dantooine</MenuItem>
                  <MenuItem value="lok">Lok</MenuItem>
                  <MenuItem value="yavin4">Yavin 4</MenuItem>
                  <MenuItem value="rori">Rori</MenuItem>
                  <MenuItem value="talus">Talus</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  label="Category"
                >
                  <MenuItem value="">All Categories</MenuItem>
                  <MenuItem value="armor">Armor</MenuItem>
                  <MenuItem value="weapons">Weapons</MenuItem>
                  <MenuItem value="buffs">Buffs</MenuItem>
                  <MenuItem value="consumables">Consumables</MenuItem>
                  <MenuItem value="utilities">Utilities</MenuItem>
                  <MenuItem value="enhancements">Enhancements</MenuItem>
                  <MenuItem value="crafting_materials">Crafting Materials</MenuItem>
                  <MenuItem value="decorations">Decorations</MenuItem>
                  <MenuItem value="clothing">Clothing</MenuItem>
                  <MenuItem value="food">Food</MenuItem>
                  <MenuItem value="medical">Medical</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={1}>
              <TextField
                fullWidth
                label="Min Cost"
                type="number"
                value={minCostFilter}
                onChange={(e) => setMinCostFilter(e.target.value)}
                InputProps={{
                  startAdornment: <MoneyIcon sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={1}>
              <TextField
                fullWidth
                label="Max Cost"
                type="number"
                value={maxCostFilter}
                onChange={(e) => setMaxCostFilter(e.target.value)}
                InputProps={{
                  startAdornment: <MoneyIcon sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={1}>
              <Button
                fullWidth
                variant="outlined"
                onClick={clearFilters}
                startIcon={<ClearIcon />}
                sx={{ height: '56px' }}
              >
                Clear
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Statistics */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Items
              </Typography>
              <Typography variant="h4">
                {filteredAndSortedItems.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Value
              </Typography>
              <Typography variant="h4">
                {formatCost(filteredAndSortedItems.reduce((sum, item) => sum + item.cost, 0))}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Unique Vendors
              </Typography>
              <Typography variant="h4">
                {new Set(filteredAndSortedItems.map(item => item.vendor_id)).size}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Recent Discoveries
              </Typography>
              <Typography variant="h4">
                {filteredAndSortedItems.filter(item => 
                  new Date(item.timestamp) > new Date(Date.now() - 24 * 60 * 60 * 1000)
                ).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <Button
                  onClick={() => handleSort('item_name')}
                  startIcon={<SearchIcon />}
                  sx={{ textTransform: 'none' }}
                >
                  Item Name
                </Button>
              </TableCell>
              <TableCell>Category</TableCell>
              <TableCell>
                <Button
                  onClick={() => handleSort('cost')}
                  startIcon={<MoneyIcon />}
                  sx={{ textTransform: 'none' }}
                >
                  Cost
                </Button>
              </TableCell>
              <TableCell>Vendor</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Planet</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>
                <Button
                  onClick={() => handleSort('timestamp')}
                  startIcon={<TimeIcon />}
                  sx={{ textTransform: 'none' }}
                >
                  Discovered
                </Button>
              </TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedItems.map((item) => (
              <TableRow key={item.item_id} hover>
                <TableCell>
                  <Typography variant="body2" fontWeight="bold">
                    {item.item_name}
                  </Typography>
                  {item.quality && (
                    <Chip 
                      label={item.quality} 
                      size="small" 
                      color="primary" 
                      sx={{ mt: 0.5 }}
                    />
                  )}
                </TableCell>
                <TableCell>
                  <Chip label={item.category} size="small" />
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="success.main" fontWeight="bold">
                    {formatCost(item.cost)}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="primary">
                    {item.vendor_name}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={item.vendor_type} 
                    size="small" 
                    color={getVendorTypeColor(item.vendor_type) as any}
                  />
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <LocationIcon sx={{ mr: 0.5, fontSize: 'small' }} />
                    {item.planet}
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="textSecondary">
                    {item.location}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="textSecondary">
                    {formatDate(item.timestamp)}
                  </Typography>
                </TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => handleItemClick(item)}
                    title="View Item Details"
                  >
                    <VisibilityIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleVendorClick(item.vendor_id)}
                    title="View Vendor Details"
                  >
                    <StoreIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      <Box display="flex" justifyContent="center" mt={2}>
        <Pagination
          count={Math.ceil(filteredAndSortedItems.length / rowsPerPage)}
          page={page}
          onChange={(_, newPage) => setPage(newPage)}
          color="primary"
        />
      </Box>

      {/* Item Details Modal */}
      <Dialog open={itemModalOpen} onClose={() => setItemModalOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedItem?.item_name}
        </DialogTitle>
        <DialogContent>
          {selectedItem && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Item Information</Typography>
                <Typography><strong>Category:</strong> {selectedItem.category}</Typography>
                <Typography><strong>Cost:</strong> {formatCost(selectedItem.cost)}</Typography>
                <Typography><strong>Quality:</strong> {selectedItem.quality || 'Standard'}</Typography>
                <Typography><strong>Discovered:</strong> {formatDate(selectedItem.timestamp)}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Vendor Information</Typography>
                <Typography><strong>Vendor:</strong> {selectedItem.vendor_name}</Typography>
                <Typography><strong>Type:</strong> {selectedItem.vendor_type}</Typography>
                <Typography><strong>Location:</strong> {selectedItem.location}, {selectedItem.planet}</Typography>
              </Grid>
              {selectedItem.stats && Object.keys(selectedItem.stats).length > 0 && (
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>Stats</Typography>
                  {Object.entries(selectedItem.stats).map(([key, value]) => (
                    <Typography key={key}><strong>{key}:</strong> {value}</Typography>
                  ))}
                </Grid>
              )}
              {selectedItem.resists && Object.keys(selectedItem.resists).length > 0 && (
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>Resists</Typography>
                  {Object.entries(selectedItem.resists).map(([key, value]) => (
                    <Typography key={key}><strong>{key} Resist:</strong> {value}</Typography>
                  ))}
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setItemModalOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Vendor Details Modal */}
      <Dialog open={vendorModalOpen} onClose={() => setVendorModalOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedVendor?.vendor_name}
        </DialogTitle>
        <DialogContent>
          {selectedVendor && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Vendor Information</Typography>
                <Typography><strong>Type:</strong> {selectedVendor.vendor_type}</Typography>
                <Typography><strong>Location:</strong> {selectedVendor.location}, {selectedVendor.planet}</Typography>
                <Typography><strong>First Discovered:</strong> {formatDate(selectedVendor.first_discovered)}</Typography>
                <Typography><strong>Last Visited:</strong> {formatDate(selectedVendor.last_visited)}</Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>Statistics</Typography>
                <Typography><strong>Total Visits:</strong> {selectedVendor.total_visits}</Typography>
                <Typography><strong>Items Discovered:</strong> {selectedVendor.items_discovered}</Typography>
                <Typography><strong>Average Cost:</strong> {formatCost(selectedVendor.average_item_cost)}</Typography>
                <Typography><strong>Most Expensive:</strong> {selectedVendor.most_expensive_item} ({formatCost(selectedVendor.most_expensive_cost)})</Typography>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVendorModalOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default VendorDiscoveryTable; 