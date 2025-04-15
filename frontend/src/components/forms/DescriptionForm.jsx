import * as React from 'react';
import TextField from '@mui/material/TextField';

export default function DescriptionForm({label,rows,label,value,name,onChange,onBlur,helperText,error}) {
  return (
        <TextField
          id="outlined-multiline-static"
          sx={{width:'100%'}}
          label={label}
          multiline
          rows={rows}
          name = {name}
          onChange={onChange}
          onBlur={onBlur}
          error={error} // to show error state of the form turn in red 
          helperText={helperText} // show error message
          
        />
      
  );
}