import * as React from 'react';
import TextField from '@mui/material/TextField';

export default function TextForm({label,value,name,onChange,onBlur ,...props}) {
  return (
      <TextField 
            id="standard-basic" 
            sx={{width:'100%'}}
            label={label}
            variant="outlined"
            value = {value}
            {...props}
            name = {name}
            onChange={onChange}
            onBlur={onBlur}
            
        />
   
  );
}