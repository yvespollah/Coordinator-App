import {React, useState, useEffect} from 'react'
import AxiosInstance from './axios'
import {Box, Typography, Button} from '@mui/material'
import AddBoxIcon from '@mui/icons-material/AddBox';
import { useNavigate, useParams } from 'react-router-dom';
import MyMessage from './forms/Message';

const Delete = () =>{

    const [message, setMessage] = useState([])
    const navigate = useNavigate()  

    const [managerData, setManagers] = useState({
      username: "",
      email: "",
      status: "",
    }
    )

    const MyParameter = useParams()
    const MyId = MyParameter.id


    const GetData = () =>{
        AxiosInstance.get(`managers/${MyId}/`).then((res) =>{
          setManagers(res.data)
        } )
    }

    useEffect(() =>{
        GetData()
    },[])

    const DeleteRecord = (event) => {
        event.preventDefault() // avoid the page to reload when we make a request
        AxiosInstance.delete(`managers/${MyId}/`)
        .then(()=>{
            setMessage(
                <MyMessage
                    messageText = {"You succesfully deleted data in the database!"}
                    messagecolor = {"green"}
                /> 
            )
            setTimeout(()=>{
                navigate('/manager')
            },1000)

        } )
    }

    return(
        <div>
            <form onSubmit={DeleteRecord}>
             {message}
             <Box className={"Topbar"}>
                <AddBoxIcon/>
                <Typography sx={{marginLeft:'15px', fontWeight:'bold'}} variant='subtitle2'>Are you sure that you want to delete this record?</Typography>
            </Box>

            <Box className={'TextBox'}>
                <Typography>
                     You will be deleting the manager <strong>{managerData.username}</strong>.
                </Typography>
            </Box>

            <Box sx={{marginTop:'30px'}}>
                <Button type="submit" variant="contained" fullWidth>Delete</Button>
            </Box>

            </form>
        </div>
    )
}

export default Delete