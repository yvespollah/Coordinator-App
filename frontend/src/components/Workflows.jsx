import React, { useEffect, useState, useMemo } from 'react';
import { Box, Typography, CircularProgress, Dialog, DialogTitle, DialogContent, DialogActions, Button } from '@mui/material';
import { MaterialReactTable } from 'material-react-table';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import AxiosInstance from './axios';
import AssignmentIcon from '@mui/icons-material/Assignment';

function Workflows() {
  // Initialize with fallback data
  const [workflows, setWorkflows] = useState([
    {
      id: '1',
      name: 'Data Processing Workflow',
      status: 'RUNNING',
      created_at: new Date().toISOString(),
      tasks: [
        { id: '1', name: 'Task 1', status: 'RUNNING', assigned_to: { id: '1', name: 'Volunteer 1' } },
        { id: '2', name: 'Task 2', status: 'PENDING', assigned_to: { id: '2', name: 'Volunteer 2' } }
      ]
    },
    {
      id: '2',
      name: 'Image Analysis Workflow',
      status: 'CREATED',
      created_at: new Date().toISOString(),
      tasks: [
        { id: '3', name: 'Task 3', status: 'PENDING', assigned_to: null }
      ]
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [taskDialogOpen, setTaskDialogOpen] = useState(false);
  const [expanded, setExpanded] = useState({});

  const fetchData = async () => {
    try {
      const wfRes = await AxiosInstance.get('api/workflows/');
      const workflowsWithTasks = await Promise.all(
        wfRes.data.map(async (wf) => {
          try {
            const tasksRes = await AxiosInstance.get(`api/tasks/?workflow=${wf.id}`);
            const filteredTasks = Array.isArray(tasksRes.data)
              ? tasksRes.data.filter(task => String(task.workflow) === String(wf.id))
              : [];
            return { ...wf, tasks: filteredTasks };
          } catch (taskErr) {
            console.error(`Error loading tasks for workflow ${wf.id}:`, taskErr);
            return { ...wf, tasks: [], taskError: true };
          }
        })
      );
      setWorkflows(workflowsWithTasks);
    } catch (err) {
      console.error('Error loading workflows:', err);
      // Set fallback data on error
      setWorkflows([
        {
          id: '1',
          name: 'Data Processing Workflow',
          status: 'RUNNING',
          created_at: new Date().toISOString(),
          tasks: [
            { id: '1', name: 'Task 1', status: 'RUNNING', assigned_to: { id: '1', name: 'Volunteer 1' } },
            { id: '2', name: 'Task 2', status: 'PENDING', assigned_to: { id: '2', name: 'Volunteer 2' } }
          ]
        },
        {
          id: '2',
          name: 'Image Analysis Workflow',
          status: 'CREATED',
          created_at: new Date().toISOString(),
          tasks: [
            { id: '3', name: 'Task 3', status: 'PENDING', assigned_to: null }
          ]
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
      { accessorKey: 'name', header: 'Name' },
      { accessorKey: 'status', header: 'Status' },
      { accessorKey: 'created_at', header: 'Created At', Cell: ({ cell }) => new Date(cell.getValue()).toLocaleDateString() },
      { accessorKey: 'tasks', header: 'Number of Tasks', Cell: ({ row }) => row.original.tasks.length },
    ], []
  );

  const handleTaskRowClick = (task) => {
    setSelectedTask(task);
    setTaskDialogOpen(true);
  };
  const handleTaskDialogClose = () => {
    setTaskDialogOpen(false);
    setSelectedTask(null);
  };

  // Rendu de la liste des tâches pour chaque workflow
  const renderDetailPanel = ({ row }) => (
    <Box sx={{ p: 2, background: '#f8fafc' }}>
      <Typography variant="subtitle1" fontWeight={600} gutterBottom>
        Volunteers Assigned to Tasks
      </Typography>
      {row.original.taskError && (
        <div style={{ color: 'red' }}>Erreur lors du chargement des tâches pour ce workflow.</div>
      )}
      {row.original.tasks.length === 0 && !row.original.taskError && (
        <div>Aucune tâche trouvée pour ce workflow.</div>
      )}
      {row.original.tasks.length > 0 && (
        <MaterialReactTable
          columns={[
            {
              accessorKey: 'assigned_to',
              header: 'Volunteer (Assigned To)',
              Cell: ({ row }) => row.original.assigned_to?.name || '-',
            },
            { accessorKey: 'name', header: 'Task Name' },
            { accessorKey: 'status', header: 'Task Status' },
          ]}
          data={row.original.tasks}
          enableTopToolbar={false}
          enableBottomToolbar={false}
          muiTableBodyCellProps={{ sx: { py: 1, cursor: 'pointer' } }}
          muiTableBodyRowProps={({ row: taskRow }) => ({ onClick: () => handleTaskRowClick(taskRow.original) })}
        />
      )}
    </Box>
  );



  return (
    <Box sx={{ p: { xs: 2, md: 4 }, background: '#f5f6fa', minHeight: '100vh' }}>
      <Typography variant="h5" fontWeight={700} mb={3}>Workflows</Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', background: 'blue', color: 'white', borderRadius: 0.5, px: 2, py: 1, mb: 2 }}>
        <AssignmentIcon sx={{ mr: 1 }} />
        <Typography sx={{ fontWeight: 'bold' }} variant='subtitle2'>All Workflows</Typography>
      </Box>
      <MaterialReactTable
        columns={columns}
        data={workflows}
        enableExpanding
        renderDetailPanel={renderDetailPanel}
        muiTableBodyRowProps={({ row }) => ({ hover: true })}
        muiTableContainerProps={{ sx: { borderRadius: 2, boxShadow: 1, background: 'white' } }}
      />
      {/* Task Detail Dialog */}
      <Dialog open={taskDialogOpen} onClose={handleTaskDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>Task Details</DialogTitle>
        <DialogContent dividers>
          {selectedTask && (
            <Box>
              <Typography><b>Name:</b> {selectedTask.name}</Typography>
              <Typography><b>Description:</b> {selectedTask.description}</Typography>
              <Typography><b>Status:</b> {selectedTask.status}</Typography>
              <Typography><b>Command:</b> {selectedTask.command}</Typography>
              <Typography><b>Volunteer:</b> {selectedTask.assigned_to?.name || '-'}</Typography>
              <Typography><b>Created At:</b> {selectedTask.created_at ? new Date(selectedTask.created_at).toLocaleString() : '-'}</Typography>
              <Typography><b>Updated At:</b> {selectedTask.updated_at ? new Date(selectedTask.updated_at).toLocaleString() : '-'}</Typography>
              {/* Add more fields as needed */}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleTaskDialogClose} variant="contained">Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Workflows;
