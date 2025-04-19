import {React, useState, useEffect} from 'react'
import AxiosInstance from './axios'
import {Box, Typography} from '@mui/material'
import AddBoxIcon from '@mui/icons-material/AddBox';
import TextForm from './forms/TextForm';
import SelectForm from './forms/SelectForm';
import Button from '@mui/material/Button'
import {useFormik} from 'formik'
import * as Yup from 'yup';
import MyMessage from './forms/Message';
import { useNavigate,useParams } from 'react-router-dom';

const Edit = () =>{
    const [managerData, setManagers] = useState({
      username: "",
      email: "",
      status: "",
    }
    )
    const [workflow, setWorkflows] = useState([])
    const [task, setTask] = useState([])
    const [machine, setMachines] = useState([])
    const [availabilities, setAvailabilities] = useState([])
    const [message, setMessage] = useState([])
    const navigate = useNavigate()  

    const MyParameter = useParams()
    const MyId = MyParameter.id


    const GetData = () =>{
        AxiosInstance.get(`managers/${MyId}/`).then((res) =>{
          setManagers(res.data)
        } )

        AxiosInstance.get(`workflows/`).then((res) =>{
          setWorkflows(res.data)
        } )

        AxiosInstance.get(`tasks/`).then((res) =>{
          setTask(res.data)
        } )

        AxiosInstance.get(`machines/`).then((res) =>{
          setMachines(res.data)
      } )

      AxiosInstance.get(`availabilities/`).then((res) =>{
        setAvailabilities(res.data)
    } )
    }

    useEffect(() =>{
        GetData()
    },[])

    // defining rule
    
    const validationSchema = Yup.object({
      username: Yup
        .string("The name must be a text")
        .required("The name is required"),
      email: Yup
        .string("The email must be a text")
        .email("The email must be a valid email")
        .required("The email is required"),
      status: Yup.string().required("Status is required"),

    })  

    const formik = useFormik({
      
      initialValues:{
        username:managerData.username,
        email:managerData.email,
        status:managerData.status,
   

      },
      enableReinitialize: true,
      validationSchema: validationSchema,
      
      onSubmit:(values) => {
        AxiosInstance.  put(`managers/${MyId}/`,values)
        .then(()=>{
          setMessage(
          <MyMessage
            messageText={"Update succesfull"}
            messagecolor={"green"}
          />
        )
        setTimeout(() => {
          navigate('/manager')
        },1000)
      })
    }
    })

    const statusOptions = [
      { value: 'active', label: 'Active' },
      { value: 'inactive', label: 'Inactive' },
      { value: 'suspended', label: 'Suspended' },
    ];

    return(
        <div>
          <form onSubmit={formik.handleSubmit}>
            <Box className="Topbar">
              <AddBoxIcon />
              <Typography sx={{marginLeft:'15px', fontWeight:'bold'}} variant='subtitle1'>Edit Manager information</Typography>
            </Box>

            {message}

            <Box className={'FormBox'}>
                
                <Box className={'FormArea'}>
                <Box sx={{marginTop:'30px'}}>
                    <TextForm
                        label = {"Username"}
                        name = 'username'
                        value={formik.values.username}
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                        error={formik.touched.username && Boolean(formik.errors.username)}
                        helperText={formik.touched.username && formik.errors.username}
                    />
                  </Box>

                    <Box sx={{marginTop:'30px'}}>
                        <TextForm
                            label = {"Email"}
                            name = 'email'
                            value={formik.values.email}
                            onChange={formik.handleChange}
                            onBlur={formik.handleBlur}
                            error={formik.touched.email && Boolean(formik.errors.email)}
                            helperText={formik.touched.email && formik.errors.email}
                        />
                    </Box>
                    
                    
                    <Box sx={{marginTop:'30px'}}>
                        <Button type='submit' variant="contained" fullWidth>Submit the data</Button>
                    </Box>
                   

                </Box>
                

                <Box className={'FormArea'}>
                    
                    {/* <Box sx={{marginTop:'30px'}}>
                        <TextForm
                            label = {"Registration Date"}
                            type="datetime-local"
                            InputLabelProps={{ shrink: true }}
                            name = 'register_date'
                            value={formik.values.register_date}
                            onChange={formik.handleChange}
                            onBlur={formik.handleBlur}
                        />

                    </Box>

                    <Box sx={{marginTop:'30px'}}>
                        <TextForm
                            label = {"Last Login"}
                            type="datetime-local"
                            InputLabelProps={{ shrink: true }}
                            name = 'last_login'
                            value={formik.values.last_login}
                            onChange={formik.handleChange}
                            onBlur={formik.handleBlur}
                        />
                    </Box> */}

                    <Box sx={{marginTop:'30px'}}>
                        <SelectForm
                            label = {"Status"}
                            options = {statusOptions}
                            name = 'status'
                            value={formik.values.status}
                            onChange={formik.handleChange}
                            onBlur={formik.handleBlur}
                            error={formik.touched.status && Boolean(formik.errors.status)}
                            helperText={formik.touched.status && formik.errors.status}
                        />
                    </Box>                    
                </Box>

            </Box>  
            </form>
        </div>
        
    )
}

export default Edit