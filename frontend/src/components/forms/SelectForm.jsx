import * as React from 'react';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';

export default function SelectForm({label,options,value,name,onChange,onBlur,error,helperText}) {

  return (
      <FormControl fullWidth>
        <InputLabel id="demo-simple-select-label">{label}</InputLabel>
        <Select
          labelId="demo-simple-select-label"
          id="demo-simple-select"
          label={label}
          value = {value}
          name = {name}
          onChange={onChange}
          onBlur={onBlur}
          error={error} // to show error state of the form turn in red 
          helperText={helperText} // show error message
        >

          {
            options.map((option) =>(
                <MenuItem value={option.value}>{option.label}</MenuItem>
            ))
          }
          
        </Select>
      </FormControl>
  );
}