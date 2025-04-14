import {React, useState, useEffect} from 'react'
import AxiosInstance from './axios'
import {Box, Typography} from '@mui/material'
import AddBoxIcon from '@mui/icons-material/AddBox';
import TextForm from './forms/TextForm';
import SelectForm from './forms/SelectForm';
import Button from '@mui/material/Button'
import {useFormik} from 'formik'


const Create = () =>{
    const [manager, setManagers] = useState([])
    const [workflow, setWorkflows] = useState([])
    const [task, setTask] = useState([])
    const [machine, setMachines] = useState([])
    const [availabilities, setAvailabilities] = useState([])

    console.log( "manager",manager)


    const GetData = () =>{
        AxiosInstance.get(`managers/`).then((res) =>{
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

    const formik = useFormik({
      initialValues:{
        username: "",
        email: "",
        password: "",
        registration_date: "",

      },
      onSubmit:(values) => {
        AxiosInstance.post(`managers/`,values)
        .then(()=>{
          console.log("Successfull data submission")
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
              <AddBoxIcon></AddBoxIcon>
              <Typography sx={{marginLeft:'15px', fontWeight:'bold'}} variant='subtitle1'>Create Manager</Typography>
            </Box>

            <Box className={'FormBox'}>
                
                <Box className={'FormArea'}>
                <Box sx={{marginTop:'30px'}}>
                    <TextForm
                        label = {"Username"}
                        name = 'username'
                        value={formik.values.username}
                        onChange={formik.handleChange}
                        onBlur={formik.handleBlur}
                    />
                  </Box>

                    <Box sx={{marginTop:'30px'}}>
                        <TextForm
                            label = {"Email"}
                            name = 'email'
                            value={formik.values.email}
                            onChange={formik.handleChange}
                            onBlur={formik.handleBlur}
                        />
                    </Box>

                    <Box sx={{marginTop:'30px'}}>
                        <TextForm
                            label = {"Password"}
                            name = 'password'
                            value={formik.values.password}
                            onChange={formik.handleChange}
                            onBlur={formik.handleBlur}
                        />
                    </Box>
                    
                    
                    <Box sx={{marginTop:'30px'}}>
                        <Button type='submit' variant="contained" fullWidth>Submit the data</Button>
                    </Box>
                   

                </Box>
                

                <Box className={'FormArea'}>
                    
                    <Box sx={{marginTop:'30px'}}>
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
                    </Box>

                    <Box sx={{marginTop:'30px'}}>
                        <SelectForm
                            label = {"Status"}
                            options = {statusOptions}
                            name = 'status'
                            value={formik.values.status}
                            onChange={formik.handleChange}
                            onBlur={formik.handleBlur}
                        />
                    </Box>                      
                </Box>

            </Box>  
            </form>
        </div>
        
    )
}

export default Create