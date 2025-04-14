import * as React from 'react';
import TextField from '@mui/material/TextField';

export default function DescriptionForm({label,rows,label,value,name,onChange,onBlur}) {
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
          
        />
      
  );
}