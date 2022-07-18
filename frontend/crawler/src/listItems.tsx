import * as React from 'react';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import SitesIcon from '@mui/icons-material/Web';
import ExecutionIcon from '@mui/icons-material/Settings';
import VisualisationIcon from '@mui/icons-material/AutoGraph';
import { Link } from 'react-router-dom';

export const mainListItems = (
  <React.Fragment>
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
    <ListItemButton component={Link} to={'/visualisation'}>
      <ListItemIcon>
        <VisualisationIcon />
      </ListItemIcon>
      <ListItemText primary="Visualisation" />
    </ListItemButton>
  </React.Fragment>
);
