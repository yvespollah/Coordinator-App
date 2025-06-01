import {React, useEffect, useMemo,useState} from 'react'
import {Box,Typography,Drawer,IconButton,Divider,Card,CardContent,Avatar,Chip,Stack, Button, Toolbar, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Tooltip} from '@mui/material'
import CalendarViewMonthIcon from '@mui/icons-material/CalendarViewMonth';
import CloseIcon from '@mui/icons-material/Close';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import DeleteIcon from '@mui/icons-material/Delete';
import PersonIcon from '@mui/icons-material/Person';
import MemoryIcon from '@mui/icons-material/Memory';
import StorageIcon from '@mui/icons-material/Storage';
import ComputerIcon from '@mui/icons-material/Computer';
import DnsIcon from '@mui/icons-material/Dns';
import LanIcon from '@mui/icons-material/Lan';
import {MaterialReactTable} from 'material-react-table';
import AxiosInstance from './axios';

const Volunteer = () =>{

    // Initialize with fallback data
    const [myData, setMyData] = useState([
      { id: '1', name: 'Volunteer 1', status: 'available', last_update: new Date().toISOString(), last_activity: new Date().toISOString(), cpu_model: 'Intel i7', total_ram: 16000 },
      { id: '2', name: 'Volunteer 2', status: 'available', last_update: new Date().toISOString(), last_activity: new Date().toISOString(), cpu_model: 'AMD Ryzen 5', total_ram: 8000 },
      { id: '3', name: 'Volunteer 3', status: 'available', last_update: new Date().toISOString(), last_activity: new Date().toISOString(), cpu_model: 'Intel i5', total_ram: 4000 }
    ]);
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [selectedVolunteer, setSelectedVolunteer] = useState(null);
    const [deleteId, setDeleteId] = useState(null);

    const fetchData = () => {
      AxiosInstance.get(`api/volunteers/`).then((res) => {
        setMyData(res.data);
      }).catch(error => {
        console.error("Error fetching volunteers:", error);
        // Set fallback data on error
        setMyData([
          { id: '1', name: 'Volunteer 1', status: 'available', last_update: new Date().toISOString(), last_activity: new Date().toISOString(), cpu_model: 'Intel i7', total_ram: 16000 },
          { id: '2', name: 'Volunteer 2', status: 'available', last_update: new Date().toISOString(), last_activity: new Date().toISOString(), cpu_model: 'AMD Ryzen 5', total_ram: 8000 },
          { id: '3', name: 'Volunteer 3', status: 'available', last_update: new Date().toISOString(), last_activity: new Date().toISOString(), cpu_model: 'Intel i5', total_ram: 4000 }
        ]);
      });
    };

    useEffect(() => {
      // Initial fetch
      fetchData();

      // Set up interval for real-time updates every 2 seconds
      const interval = setInterval(fetchData, 2000);

      // Cleanup interval on component unmount
      return () => clearInterval(interval);
    }, []);

    const columns = useMemo(
        () => [
            {accessorKey:'name', header: 'Name'},
            {accessorKey:'status', header: 'Status'},
            {accessorKey:'last_update', header: 'Last Update', Cell: ({ cell }) => {const date = new Date(cell.getValue());return date.toLocaleDateString();}},
            {accessorKey:'last_activity', header: 'Last Activity', Cell: ({ cell }) => cell.getValue() ? new Date(cell.getValue()).toLocaleString() : '—'},
            {accessorKey:'cpu_model', header: 'CPU'},
            {accessorKey:'total_ram', header: 'RAM (MB)'},
            {
                header: 'Actions',
                Cell: ({ row }) => (
                    <Stack direction="row" spacing={1}>
                        <Tooltip title="Delete"><IconButton  onClick={e => {e.stopPropagation(); handleDelete(row.original.id);}}><DeleteIcon color="error" fontSize="small" /></IconButton></Tooltip>
                    </Stack>
                ),
                enableColumnActions: false,
                enableSorting: false,
                size: 80,
            }
        ],[])

    const handleRowClick = (row) => {
        setSelectedVolunteer(row.original);
        setDrawerOpen(true);
    };

    const handleDrawerClose = () => {
        setDrawerOpen(false);
        setSelectedVolunteer(null);
    };

    const handleDelete = (id) => {
        setDeleteId(id);
        if(window.confirm('Are you sure you want to delete this volunteer?')){
            AxiosInstance.delete(`api/volunteers/${id}/`).then(() => GetData())
                .catch(error => {
                    console.error("Error deleting volunteer:", error);
                });
        }
    };

    return (
        <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', background: 'blue', color: 'white', borderRadius: 0.5, px: 2, py: 1, mb: 2 }}>
                <CalendarViewMonthIcon sx={{ mr: 1 }} />
                <Typography sx={{ fontWeight: 'bold' }} variant='subtitle2'>All Volunteers</Typography>
            </Box>
            <MaterialReactTable
                columns={columns}
                data={myData}
                muiTableBodyRowProps={({ row }) => ({
                    onClick: () => handleRowClick(row),
                    style: { cursor: 'pointer' },
                })}
            />
            {/* Drawer for details */}
            <Drawer anchor="right" open={drawerOpen} onClose={handleDrawerClose}>
                <Box sx={{ width: 400, p: 0, bgcolor: '#f7f9fa', height: '100%' }}>
                    {/* Drawer Header */}
                    <Box sx={{display: 'flex', alignItems: 'center', justifyContent: 'space-between',bgcolor: '#1976d2', color: 'white', px: 3, py: 2}}>
                        <Stack direction="row" alignItems="center" spacing={2}>
                            <Avatar sx={{ bgcolor: '#fff', color: '#1976d2' }}><PersonIcon /></Avatar>
                            <Typography variant="h6" sx={{ fontWeight: 600 }}>Volunteer Details</Typography>
                        </Stack>
                        <IconButton onClick={handleDrawerClose} sx={{ color: 'white' }}><CloseIcon /></IconButton>
                    </Box>
                    <Card sx={{ m: 3, boxShadow: 2 }}>
                        <CardContent>
                            {selectedVolunteer && (
                                <Box>
                                    {/* General Info Section */}
                                    <Typography variant="subtitle1" sx={{ fontWeight: 500, mb: 1 }}>General</Typography>
                                    <Divider sx={{ mb: 2 }} />
                                    <Stack direction="row" alignItems="center" spacing={2} mb={2}>
                                        <Avatar sx={{ bgcolor: '#1976d2', color: 'white', width: 48, height: 48, fontSize: 24 }}>
                                            {selectedVolunteer.name ? selectedVolunteer.name[0].toUpperCase() : '?'}
                                        </Avatar>
                                        <Box>
                                            <Typography variant="h6">{selectedVolunteer.name}</Typography>
                                            <Chip label={selectedVolunteer.current_status} color={selectedVolunteer.current_status === 'available' ? 'success' : 'default'} size="small" sx={{ mt: 1 }} />
                                        </Box>
                                    </Stack>
                                    <Typography color="text.secondary" sx={{ mb: 2 }}>Last Update: {new Date(selectedVolunteer.last_update).toLocaleString()}</Typography>
                                    <Typography color="text.secondary" sx={{ mb: 2 }}>Last Activity: {selectedVolunteer.last_activity ? new Date(selectedVolunteer.last_activity).toLocaleString() : '—'}</Typography>
                                    {/* Hardware Section */}
                                    <Typography variant="subtitle1" sx={{ fontWeight: 500, mt: 2, mb: 1 }}><MemoryIcon fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} /> Hardware</Typography>
                                    <Divider sx={{ mb: 2 }} />
                                    <Stack spacing={1}>
                                        <Typography><b>CPU Model:</b> {selectedVolunteer.cpu_model}</Typography>
                                        <Typography><b>CPU Cores:</b> {selectedVolunteer.cpu_cores}</Typography>
                                        <Typography><b>Total RAM:</b> {selectedVolunteer.total_ram}</Typography>
                                        <Typography><b>Available Storage:</b> {selectedVolunteer.available_storage}</Typography>
                                        <Typography><b>Operating System:</b> {selectedVolunteer.operating_system}</Typography>
                                        <Typography><b>GPU Available:</b> {selectedVolunteer.gpu_available ? 'Yes' : 'No'}</Typography>
                                        <Typography><b>GPU Model:</b> {selectedVolunteer.gpu_model}</Typography>
                                        <Typography><b>GPU Memory:</b> {selectedVolunteer.gpu_memory}</Typography>
                                    </Stack>
                                    {/* Network Section */}
                                    <Typography variant="subtitle1" sx={{ fontWeight: 500, mt: 3, mb: 1 }}><LanIcon fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} /> Network</Typography>
                                    <Divider sx={{ mb: 2 }} />
                                    <Stack spacing={1}>
                                        <Typography><b>IP Address:</b> {selectedVolunteer.ip_address}</Typography>
                                        <Typography><b>Communication Port:</b> {selectedVolunteer.communication_port}</Typography>
                                    </Stack>
                                    {/* Preferences Section */}
                                    <Typography variant="subtitle1" sx={{ fontWeight: 500, mt: 3, mb: 1 }}><DnsIcon fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} /> Preferences</Typography>
                                    <Divider sx={{ mb: 2 }} />
                                    <Typography>{JSON.stringify(selectedVolunteer.preferences)}</Typography>
                                </Box>
                            )}
                        </CardContent>
                    </Card>
                </Box>
            </Drawer>
        </Box>
    )
}

export default Volunteer