import * as React from 'react';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SitesIcon from '@mui/icons-material/Web';
import ExecutionIcon from '@mui/icons-material/Settings';
import MonitorIcon from '@mui/icons-material/MonitorHeartOutlined';
import VisualisationIcon from '@mui/icons-material/AutoGraph';
import { Link } from 'react-router-dom';

export const mainListItems = (
  <React.Fragment>
    <ListItemButton component={Link} to={'/home'}>
      <ListItemIcon>
        <DashboardIcon />
      </ListItemIcon>
      <ListItemText primary="Dashboard" />
    </ListItemButton>
    <ListItemButton component={Link} to={'/sites'}>
      <ListItemIcon>
        <SitesIcon />
      </ListItemIcon>
      <ListItemText primary="Sites" />
    </ListItemButton>
    <ListItemButton component={Link} to={'/executions'}>
      <ListItemIcon>
        <ExecutionIcon />
      </ListItemIcon>
      <ListItemText primary="Executions" />
    </ListItemButton>
    <ListItemButton>
      <ListItemIcon>
        <VisualisationIcon />
      </ListItemIcon>
      <ListItemText primary="Visualisation" />
    </ListItemButton>
    <ListItemButton>
      <ListItemIcon>
        <MonitorIcon />
      </ListItemIcon>
      <ListItemText primary="Monitoring" />
    </ListItemButton>
  </React.Fragment>
);
