import React, { useEffect, useState, useMemo } from 'react';
import { Box, Typography, CircularProgress, Dialog, DialogTitle, DialogContent, DialogActions, Button } from '@mui/material';
import { MaterialReactTable } from 'material-react-table';
import AxiosInstance from './axios';
import AssignmentIcon from '@mui/icons-material/Assignment';

const Tasks = () => {
  // Initialize with fallback data
  const [tasks, setTasks] = useState([
    {
      id: '1',
      name: 'Data Processing Task',
      status: 'RUNNING',
      workflow: { id: '1', name: 'Data Processing Workflow' },
      assigned_to: { id: '1', name: 'Volunteer 1' },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: '2',
      name: 'Image Analysis Task',
      status: 'PENDING',
      workflow: { id: '2', name: 'Image Analysis Workflow' },
      assigned_to: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ]);

  const fetchData = async () => {
    try {
      const res = await AxiosInstance.get('api/tasks/');
      setTasks(res.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      // Set fallback data on error
      setTasks([
        {
          id: '1',
          name: 'Data Processing Task',
          status: 'RUNNING',
          workflow: { id: '1', name: 'Data Processing Workflow' },
          assigned_to: { id: '1', name: 'Volunteer 1' },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: '2',
          name: 'Image Analysis Task',
          status: 'PENDING',
          workflow: { id: '2', name: 'Image Analysis Workflow' },
          assigned_to: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ]);
    }
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
      { accessorKey: 'name', header: 'Task Name' },
      { accessorKey: 'status', header: 'Status' },
      { 
        accessorKey: 'workflow', 
        header: 'Workflow',
        Cell: ({ cell }) => cell.getValue()?.name || '-' 
      },
      { 
        accessorKey: 'assigned_to', 
        header: 'Volunteer Assigned',
        Cell: ({ cell, row }) => {
          const assigned = row.original.assigned_to;
          if (assigned && typeof assigned === 'object' && assigned.name) {
            return assigned.name;
          }
          return assigned || '-';
        }
      },
      { 
        accessorKey: 'created_at', 
        header: 'Created At',
        Cell: ({ cell }) => new Date(cell.getValue()).toLocaleDateString() 
      },
      { 
        accessorKey: 'updated_at', 
        header: 'Updated At',
        Cell: ({ cell }) => new Date(cell.getValue()).toLocaleDateString() 
      }
    ],
    []
  );

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, background: '#f5f6fa', minHeight: '100vh' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', background: 'blue', color: 'white', borderRadius: 0.5, px: 2, py: 1, mb: 2 }}>
        <AssignmentIcon sx={{ mr: 1 }} />
        <Typography sx={{ fontWeight: 'bold' }} variant='subtitle2'>All Tasks</Typography>
      </Box>
      <MaterialReactTable
        columns={columns}
        data={tasks}
      />
    </Box>
  );
};

export default Tasks;
