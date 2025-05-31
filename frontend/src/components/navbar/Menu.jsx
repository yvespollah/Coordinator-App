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
import AssignmentIcon from '@mui/icons-material/Assignment';
import ListAltIcon from '@mui/icons-material/ListAlt';
import BarChartIcon from '@mui/icons-material/BarChart';
import NotificationsIcon from '@mui/icons-material/Notifications';
import ForumIcon from '@mui/icons-material/Forum';
import SettingsIcon from '@mui/icons-material/Settings';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import SettingsInputAntennaIcon from '@mui/icons-material/SettingsInputAntenna';
import DevicesIcon from '@mui/icons-material/Devices';
import {Link, useLocation} from 'react-router-dom' // for links
import { useState } from 'react';


export default function Menu() {
  const [openManager, setOpenManager] = useState(false);
  const [openVolunteer, setOpenVolunteer] = useState(false);
  const [openWorkflows, setOpenWorkflows] = useState(false);
  const [openCommunication, setOpenCommunication] = useState(false);

  const handleManagerClick = () => {
    setOpenManager(!openManager);
  };
  
  const handleVolunteerClick = () => {
    setOpenVolunteer(!openVolunteer);
  };

  const handleWorkflowsClick = () => {
    setOpenWorkflows(!openWorkflows);
  };
  
  const handleCommunicationClick = () => {
    setOpenCommunication(!openCommunication);
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

    {/* Home */}
    <ListItemButton component={Link} to="/" selected={path === "/"}>
        <ListItemIcon>
            <HomeIcon />
        </ListItemIcon>
        <ListItemText primary="Home" />
    </ListItemButton>

    {/* Managers */}
    <ListItemButton onClick={handleManagerClick}>
        <ListItemIcon>
            <DashboardIcon />
        </ListItemIcon>
        <ListItemText primary="Managers" />
        {openManager ? <ExpandLess /> : <ExpandMore />}
    </ListItemButton>
    <Collapse in={openManager} timeout="auto" unmountOnExit>
        <List component="div" disablePadding>
            <ListItemButton sx={{ pl: 4 }} component={Link} to="/manager" selected={path === "/manager"}>
                <ListItemIcon>
                    <DashboardCustomizeIcon />
                </ListItemIcon>
                <ListItemText primary="All managers" />
            </ListItemButton>

            {/* Workflows (with nested Tasks) */}
            <ListItemButton sx={{ pl: 4 }} onClick={handleWorkflowsClick}>
                <ListItemIcon>
                    <AssignmentIcon />
                </ListItemIcon>
                <ListItemText primary="Workflows" />
                {openWorkflows ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>
            <Collapse in={openWorkflows} timeout="auto" unmountOnExit>
                <List component="div" disablePadding>
                    <ListItemButton sx={{ pl: 8 }} component={Link} to="/workflows" selected={path === "/workflows"}>
                        <ListItemIcon>
                            <AssignmentIcon fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary="All Workflows" />
                    </ListItemButton>
                </List>
            </Collapse>

            <ListItemButton sx={{ pl: 4 }}>
                <ListItemIcon>
                    <DashboardCustomizeIcon />
                </ListItemIcon>
                <ListItemText primary="History of workflows" />
            </ListItemButton>
        </List>
    </Collapse>

    {/* Volunteers */}
    <ListItemButton onClick={handleVolunteerClick}>
        <ListItemIcon>
            <DashboardIcon />
        </ListItemIcon>
        <ListItemText primary="Volunteers" />
        {openVolunteer ? <ExpandLess /> : <ExpandMore />}
    </ListItemButton>
    <Collapse in={openVolunteer} timeout="auto" unmountOnExit>
        <List component="div" disablePadding>
            <ListItemButton sx={{ pl: 4 }} component={Link} to="/volunteer">
                <ListItemIcon>
                    <DashboardCustomizeIcon />
                </ListItemIcon >
                <ListItemText primary="All Volunteers" />
            </ListItemButton>
        </List>
    </Collapse>

    {/* Performance & Analytics */}
    <ListItemButton component={Link} to="/analytics" selected={path === "/analytics"}>
        <ListItemIcon>
            <BarChartIcon />
        </ListItemIcon>
        <ListItemText primary="Performance & Analytics" />
    </ListItemButton>

    {/* Notifications */}
    <ListItemButton component={Link} to="/notifications" selected={path === "/notifications"}>
        <ListItemIcon>
            <NotificationsIcon />
        </ListItemIcon>
        <ListItemText primary="Notifications" />
    </ListItemButton>

    {/* Communication/Logs */}
    <ListItemButton onClick={handleCommunicationClick}>
        <ListItemIcon>
            <ForumIcon />
        </ListItemIcon>
        <ListItemText primary="Communication" />
        {openCommunication ? <ExpandLess /> : <ExpandMore />}
    </ListItemButton>
    <Collapse in={openCommunication} timeout="auto" unmountOnExit>
        <List component="div" disablePadding>
            {/* <ListItemButton sx={{ pl: 4 }} component={Link} to="/logs" selected={path === "/logs"}>
                <ListItemIcon>
                    <ForumIcon />
                </ListItemIcon>
                <ListItemText primary="Logs" />
            </ListItemButton> */}
            {/* <ListItemButton sx={{ pl: 4 }} component={Link} to="/channel-monitor" selected={path === "/channel-monitor"}>
                <ListItemIcon>
                    <SettingsInputAntennaIcon />
                </ListItemIcon>
                <ListItemText primary="Channel Monitor" />
            </ListItemButton> */}
            <ListItemButton sx={{ pl: 4 }} component={Link} to="/system-status" selected={path === "/system-status"}>
                <ListItemIcon>
                    <DevicesIcon />
                </ListItemIcon>
                <ListItemText primary="État du Système" />
            </ListItemButton>
        </List>
    </Collapse>

    {/* Settings */}
    <ListItemButton component={Link} to="/settings" selected={path === "/settings"}>
        <ListItemIcon>
            <SettingsIcon />
        </ListItemIcon>
        <ListItemText primary="Settings" />
    </ListItemButton>

    {/* Help */}
    <ListItemButton component={Link} to="/help" selected={path === "/help"}>
        <ListItemIcon>
            <HelpOutlineIcon />
        </ListItemIcon>
        <ListItemText primary="Help" />
    </ListItemButton>
    </List>


    </>
  );
}