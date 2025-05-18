import * as React from 'react';
import TextField from '@mui/material/TextField';

export default function TextForm({label,value,name,onChange,onBlur,error,helperText,...props}) {
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
            error={error} // to show error state of the form turn in red 
            helperText={helperText} // show error message

            
        />
   
  );
}