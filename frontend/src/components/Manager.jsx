import {React, useEffect, useMemo,useState} from 'react'
import {Box, Chip, IconButton,Typography} from '@mui/material'
import {Link} from 'react-router-dom'
import CalendarViewMonthIcon from '@mui/icons-material/CalendarViewMonth';
import {MaterialReactTable} from 'material-react-table';
import AxiosInstance from './axios';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';


const Manager = () =>{

    const [myData, setMyData] = useState([])

    const GetData = () =>{
        AxiosInstance.get(`managers/`).then((res) =>{
            setMyData(res.data)
        } )
    }

    useEffect(() =>{
        GetData()
    },[])

    const columns = useMemo(
        () => [
            {
                accessorKey:'username',
                header: 'Name'
            },
            {
              accessorKey:'email',
              header: 'Email'
            },
            {
              accessorKey:'status',
              header: 'Status'
            },
            {
              accessorKey: 'registration_date',
              header: 'Registration Date',
              Cell: ({ cell }) => {
                const date = new Date(cell.getValue());
                return date.toLocaleDateString(); // Formats to 'MM/DD/YYYY' or your locale's format
              }
            },
            {
              accessorKey: 'last_login',
              header: 'Last Login',
              Cell: ({ cell }) => {
                const date = new Date(cell.getValue());
                return date.toLocaleDateString();
              }
            }
            
        ]
    )

    return(
        <div>
            <Box className={"Topbar"}>
                <CalendarViewMonthIcon/>
                <Typography sx={{marginLeft:'15px', fontWeight:'bold'}} variant='subtitle2'>All Managers</Typography>
            </Box>

            <MaterialReactTable
                columns={columns}
                data={myData}
                enableRowActions
                renderRowActions={({row}) => (
                    <Box sx={{display: 'flex',flexWrap:'nowrap', gap:'8px'}}>
                        <IconButton color="primary" component={Link} to={`edit/${row.original.id}`}> 
                            <EditIcon/>
                        </IconButton>
                        <IconButton color="error" component={Link} to={`delete/${row.original.id}`}> 
                            <DeleteIcon/>
                        </IconButton>
                    </Box>
                )
                }

            />
        </div>
    )
}

export default Manager