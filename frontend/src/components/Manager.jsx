import {React, useEffect, useMemo, useState} from 'react';
import {Box, Chip, Typography, Button, IconButton} from '@mui/material';
import {Link} from 'react-router-dom';
import CalendarViewMonthIcon from '@mui/icons-material/CalendarViewMonth';
import {MaterialReactTable} from 'material-react-table';
import AxiosInstance from './axios';
import DeleteIcon from '@mui/icons-material/Delete';

const Manager = () => {
    const [myData, setMyData] = useState([]);

    const GetData = () => {
        AxiosInstance.get(`managers/`).then((res) => {
            setMyData(res.data);
        });
    };
    console.log("----------")
    console.log(myData);

    useEffect(() => {
        GetData();
    }, []);

    const handleDelete = (id) => {
        if(window.confirm('Are you sure you want to delete this manager?')){
            AxiosInstance.delete(`managers/${id}/`).then(() => GetData());
        }
    };

    const handleToggleStatus = (manager) => {
        const newStatus = manager.status === 'active' ? 'active' : 'suspended';
        AxiosInstance.patch(`managers/${manager.id}/`, { status: newStatus })
            .then(() => GetData());
    };

    const columns = useMemo(
        () => [
            { accessorKey: 'username', header: 'Name' },
            { accessorKey: 'email', header: 'Email' },
            { accessorKey: 'status', header: 'Status' },
            { accessorKey: 'registration_date', header: 'Registration Date', Cell: ({ cell }) => { const date = new Date(cell.getValue()); return date.toLocaleDateString(); } },
            { accessorKey: 'last_login', header: 'Last Login', Cell: ({ cell }) => { const date = new Date(cell.getValue()); return date.toLocaleDateString(); } },
            {
                header: 'Actions',
                Cell: ({ row }) => (
                    <Box sx={{display: 'flex',flexWrap:'nowrap', gap:'8px'}}>
                        <Button
                            variant="outlined"
                            color={row.original.status === 'active' ? 'warning' : 'success'}
                            size="small"
                            onClick={() => handleToggleStatus(row.original)}
                        >
                            {row.original.status === 'active' ? 'Suspend' : 'Activate'}
                        </Button>
                        <IconButton color="error" onClick={() => handleDelete(row.original.id)}>
                            <DeleteIcon />
                        </IconButton>
                    </Box>
                ),
                enableColumnActions: false,
                enableSorting: false,
                size: 120,
            }
        ],
        []
    );

    return (
        <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', background: 'blue', color: 'white', borderRadius: 0.5, px: 2, py: 1, mb: 2 }}>
                <CalendarViewMonthIcon sx={{ mr: 1 }} />
                <Typography sx={{ fontWeight: 'bold' }} variant='subtitle2'>All Managers</Typography>
            </Box>
            <MaterialReactTable
                columns={columns}
                data={myData}
            />
        </Box>
    );
};

export default Manager;