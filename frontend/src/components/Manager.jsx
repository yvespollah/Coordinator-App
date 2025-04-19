import {React, useEffect, useMemo,useState} from 'react'
import {Box,Typography} from '@mui/material'
import CalendarViewMonthIcon from '@mui/icons-material/CalendarViewMonth';
import {MaterialReactTable} from 'material-react-table';
import AxiosInstance from './axios';


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

            />
        </div>
    )
}

export default Manager