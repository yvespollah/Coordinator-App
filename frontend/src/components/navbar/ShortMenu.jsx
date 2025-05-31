import * as React from 'react';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import AddBoxIcon from '@mui/icons-material/AddBox';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AssignmentIcon from '@mui/icons-material/Assignment';
import ListAltIcon from '@mui/icons-material/ListAlt';
import BarChartIcon from '@mui/icons-material/BarChart';
import NotificationsIcon from '@mui/icons-material/Notifications';
import ForumIcon from '@mui/icons-material/Forum';
import SettingsIcon from '@mui/icons-material/Settings';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import {Link, useLocation} from 'react-router-dom'


export default function ShortMenu() {

  const location = useLocation()
  const path = location.pathname
  console.log(path)

  return (
    <>
    
    <List
      sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}
      component="nav"
      aria-labelledby="nested-list-subheader"
    >
     
    
      <ListItemButton component={Link} to="/" selected={path === "/"} sx={{display:'flex', justifyContent:'center'}}>
        <ListItemIcon sx={{display:'flex', justifyContent:'center'}}>
          <DashboardIcon />
        </ListItemIcon>
      </ListItemButton>

      <ListItemButton component={Link} to="/create" selected={path === "/create"} sx={{display:'flex', justifyContent:'center'}}>
        <ListItemIcon sx={{display:'flex', justifyContent:'center'}}>
            <AddBoxIcon />
        </ListItemIcon>
      </ListItemButton>

      {/* Workflows (with nested Tasks) */}
      <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
        <ListItemButton component={Link} to="/workflows" selected={path === "/workflows"} sx={{display:'flex', justifyContent:'center'}}>
          <ListItemIcon sx={{display:'flex', justifyContent:'center'}}>
              <AssignmentIcon />
          </ListItemIcon>
        </ListItemButton>
        <ListItemButton component={Link} to="/tasks" selected={path === "/tasks"} sx={{display:'flex', justifyContent:'center', marginLeft: 16}}>
          <ListItemIcon sx={{display:'flex', justifyContent:'center'}}>
              <ListAltIcon fontSize="small" />
          </ListItemIcon>
        </ListItemButton>
      </div>

      {/* Analytics */}
      <ListItemButton component={Link} to="/analytics" selected={path === "/analytics"} sx={{display:'flex', justifyContent:'center'}}>
        <ListItemIcon sx={{display:'flex', justifyContent:'center'}}>
            <BarChartIcon />
        </ListItemIcon>
      </ListItemButton>

      {/* Notifications */}
      <ListItemButton component={Link} to="/notifications" selected={path === "/notifications"} sx={{display:'flex', justifyContent:'center'}}>
        <ListItemIcon sx={{display:'flex', justifyContent:'center'}}>
            <NotificationsIcon />
        </ListItemIcon>
      </ListItemButton>

      {/* Logs */}
      {/* <ListItemButton component={Link} to="/logs" selected={path === "/logs"} sx={{display:'flex', justifyContent:'center'}}>
        <ListItemIcon sx={{display:'flex', justifyContent:'center'}}>
            <ForumIcon />
        </ListItemIcon>
      </ListItemButton> */}

      {/* Settings */}
      <ListItemButton component={Link} to="/settings" selected={path === "/settings"} sx={{display:'flex', justifyContent:'center'}}>
        <ListItemIcon sx={{display:'flex', justifyContent:'center'}}>
            <SettingsIcon />
        </ListItemIcon>
      </ListItemButton>

      {/* Help */}
      <ListItemButton component={Link} to="/help" selected={path === "/help"} sx={{display:'flex', justifyContent:'center'}}>
        <ListItemIcon sx={{display:'flex', justifyContent:'center'}}>
            <HelpOutlineIcon />
        </ListItemIcon>
      </ListItemButton>

    </List>

    </>
  );
}