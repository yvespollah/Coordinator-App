import {React, useEffect, useMemo,useState} from 'react'
import {Box,Typography} from '@mui/material'
import CalendarViewMonthIcon from '@mui/icons-material/CalendarViewMonth';
import {MaterialReactTable} from 'material-react-table';
import AxiosInstance from './axios';


const Volunteer = () =>{

    const [myData, setMyData] = useState([])

    const GetData = () =>{
        AxiosInstance.get(`volunteers/`).then((res) =>{
            setMyData(res.data)
        } )
    }
    

    useEffect(() =>{
        GetData()
    },[])

    const columns = useMemo(
        () => [
            {
                accessorKey:'name',
                header: 'Name'
            },
            {
              accessorKey:'cpu_model',
              header: 'Cpu Model'
            },
            {
              accessorKey:'cpu_cores',
              header: 'Cpu Cores'
            },
            {
                accessorKey:'total_ram',
                header: 'Total Ram'
            },
            {
                accessorKey:'available_storage',
                header: 'Available Storage'
            },
            {
                accessorKey:'operating_system',
                header: 'Operating System'
            },
            {
                accessorKey:'gpu_available',
                header: 'Gpu Available'
                
            },
            {
                accessorKey:'current_status',
                header: 'Current Status'
            },
            {
                accessorKey:'gpu_model',
                header: 'Gpu Model '
            },
            {
                accessorKey:'gpu_memory',
                header: 'Gpu Memory'
            },
            {
                accessorKey:'ip_address',
                header: 'Ip Address'
            },
            {
                accessorKey:'communication_port',
                header: 'Communication Port'
            },
            {
                accessorKey:'last_update',
                header: 'Last Update',
                Cell: ({ cell }) => {
                    const date = new Date(cell.getValue());
                    return date.toLocaleDateString();
                  }
            },
            
        ]
    )

    return(
        <div>
            <Box className={"Topbar"}>
                <CalendarViewMonthIcon/>
                <Typography sx={{marginLeft:'15px', fontWeight:'bold'}} variant='subtitle2'>All Volunteers</Typography>
            </Box>

            <MaterialReactTable
                columns={columns}
                data={myData}

            />
        </div>
    )
}

export default Volunteer