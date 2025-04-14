import * as React from 'react';
import ListSubheader from '@mui/material/ListSubheader';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Collapse from '@mui/material/Collapse';
import AddBoxIcon from '@mui/icons-material/AddBox';
import DashboardIcon from '@mui/icons-material/Dashboard';
import DashboardCustomizeIcon from '@mui/icons-material/DashboardCustomize';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import HomeIcon from '@mui/icons-material/Home';
import {Link, useLocation} from 'react-router-dom' // for links


export default function Menu() {
  const [open, setOpen] = React.useState(false);

  const handleClick = () => {
    setOpen(!open);
  };

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


    <ListItemButton component={Link} to="/" selected={path === "/home"}>
        <ListItemIcon>
            <HomeIcon />
        </ListItemIcon>
        <ListItemText primary="Home" />
    </ListItemButton>
    
    </List>

    {/* ---------------managers------------------------------------- */}


    <List
      sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}
      component="nav"
      aria-labelledby="nested-list-subheader"
    >
     
    
      <ListItemButton onClick={handleClick} component={Link} to="/" selected={path === "/"}>
        <ListItemIcon>
          <DashboardIcon />
        </ListItemIcon>
        <ListItemText primary="Managers" />
        {open ? <ExpandLess /> : <ExpandMore />}
      </ListItemButton>
      <Collapse in={open} timeout="auto" unmountOnExit>
        <List component="div" disablePadding>

          <ListItemButton sx={{ pl: 4 }}>
            <ListItemIcon>
              <DashboardCustomizeIcon />
            </ListItemIcon>
            <ListItemText primary="Create" />
          </ListItemButton>

          <ListItemButton sx={{ pl: 4 }}>
            <ListItemIcon>
              <DashboardCustomizeIcon />
            </ListItemIcon>
            <ListItemText primary="Workflow" />
          </ListItemButton>

          <ListItemButton sx={{ pl: 4 }}>
            <ListItemIcon>
              <DashboardCustomizeIcon />
            </ListItemIcon>
            <ListItemText primary="History of workflows" />
          </ListItemButton>

        </List>
      </Collapse>
    </List>

{/* ---------------volontaires------------------------------------- */}

    <List
      sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}
      component="nav"
      aria-labelledby="nested-list-subheader"
    >
     
    
      <ListItemButton onClick={handleClick} >
        <ListItemIcon>
          <DashboardIcon />
        </ListItemIcon>
        <ListItemText primary="Volontaires" />
        {open ? <ExpandLess /> : <ExpandMore />}
      </ListItemButton>
      <Collapse in={open} timeout="auto" unmountOnExit>
        <List component="div" disablePadding>

          <ListItemButton sx={{ pl: 4 }} component={Link} to="/">
            <ListItemIcon>
              <DashboardCustomizeIcon />
            </ListItemIcon >
            <ListItemText primary="Liste Volontaires" />
          </ListItemButton>

          <ListItemButton sx={{ pl: 4 }} component={Link} to="/">
            <ListItemIcon>
              <DashboardCustomizeIcon />
            </ListItemIcon>
            <ListItemText primary="Volontaires disponible" />
          </ListItemButton>

        </List>
      </Collapse>
    </List>

    <List
    sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper' }}
    component="nav"
    aria-labelledby="nested-list-subheader"
    subheader={
    <ListSubheader component="div" id="nested-list-subheader">
        Creating records
    </ListSubheader>
    }
    >


    <ListItemButton component={Link} to="/create" selected={path === "/create"}>
        <ListItemIcon>
            <AddBoxIcon />
        </ListItemIcon>
        <ListItemText primary="Create Manager" />
    </ListItemButton>
    
    </List>

    </>
  );
}