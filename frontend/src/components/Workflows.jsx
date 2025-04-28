import React, { useEffect, useMemo, useState } from 'react';
import { Box, Typography, CircularProgress, Dialog, DialogTitle, DialogContent, DialogActions, Button } from '@mui/material';
import { MaterialReactTable } from 'material-react-table';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import AxiosInstance from './axios';
import AssignmentIcon from '@mui/icons-material/Assignment';

const Workflows = () => {
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState({});
  const [taskDialogOpen, setTaskDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const wfRes = await AxiosInstance.get('workflows/');
        // For each workflow, fetch its tasks and filter them by workflow ID just in case
        const workflowsWithTasks = await Promise.all(
          wfRes.data.map(async (wf) => {
            const tasksRes = await AxiosInstance.get(`tasks/?workflow=${wf.id}`);
            console.log("-----------------")
            console.log(tasksRes)
            // Filter tasks to ensure only tasks with correct workflow id are included
            const filteredTasks = tasksRes.data.filter(task => String(task.workflow) === String(wf.id));
            return { ...wf, tasks: filteredTasks };
          })
        );
        setWorkflows(workflowsWithTasks);
      } catch (error) {
        setWorkflows([]);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const columns = useMemo(
    () => [
      { accessorKey: 'name', header: 'Name' },
      { accessorKey: 'status', header: 'Status' },
      { accessorKey: 'created_at', header: 'Created At', Cell: ({ cell }) => new Date(cell.getValue()).toLocaleDateString() },
      { accessorKey: 'tasks', header: 'Number of Tasks', Cell: ({ row }) => row.original.tasks.length },
    ], []
  );

  // Task detail dialog
  const handleTaskRowClick = (task) => {
    setSelectedTask(task);
    setTaskDialogOpen(true);
  };
  const handleTaskDialogClose = () => {
    setTaskDialogOpen(false);
    setSelectedTask(null);
  };

  // Expandable content renderer for each workflow row
  const renderDetailPanel = ({ row }) => (
    <Box sx={{ p: 2, background: '#f8fafc' }}>
      <Typography variant="subtitle1" fontWeight={600} gutterBottom>
        Volunteers Assigned to Tasks
      </Typography>
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
    </Box>
  );

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, background: '#f5f6fa', minHeight: '100vh' }}>
      <Typography variant="h5" fontWeight={700} mb={3}>Workflows</Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', background: 'blue', color: 'white', borderRadius: 0.5, px: 2, py: 1, mb: 2 }}>
        <AssignmentIcon sx={{ mr: 1 }} />
        <Typography sx={{ fontWeight: 'bold' }} variant='subtitle2'>All Workflows</Typography>
      </Box>
      {loading ? (
        <CircularProgress />
      ) : (
        <MaterialReactTable
          columns={columns}
          data={workflows}
          enableExpanding
          renderDetailPanel={renderDetailPanel}
          muiTableBodyRowProps={({ row }) => ({ hover: true })}
          muiTableContainerProps={{ sx: { borderRadius: 2, boxShadow: 1, background: 'white' } }}
        />
      )}
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
};

export default Workflows;
