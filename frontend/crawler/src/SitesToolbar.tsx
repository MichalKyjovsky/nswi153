import * as React from 'react';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Tooltip from '@mui/material/Tooltip';
import Stack from '@mui/material/Stack';
import Addicon from '@mui/icons-material/Add';
import FilterListIcon from '@mui/icons-material/FilterList';

export interface SitesToolbarProps {
    toggleFilterList: React.Dispatch<React.SetStateAction<boolean>>;
    addButtonClick: () => void;
}

const SitesToolbar = (props: SitesToolbarProps) => {
    const { toggleFilterList, addButtonClick } = props;
    const [filterListShown, setFilterListShown] = React.useState(false);

    return (
        <Toolbar
            sx={{
                pl: { sm: 2 },
                pr: { xs: 1, sm: 1 },
            }}
        >
            <Typography
                sx={{ flex: '1 1 100%' }}
                variant="h5"
                id="tableTitle"
                component="h1"
                color="primary"
            >
                Sites
            </Typography>

            <Stack direction="row" spacing={2}>
                <Tooltip title="Filter list">
                    <IconButton onClick={() => {
                        let toggled = !filterListShown;
                        toggleFilterList(toggled);
                        setFilterListShown(toggled);
                    }}>
                        <FilterListIcon />
                    </IconButton>
                </Tooltip>
                <Tooltip title="Add new website">
                    <IconButton onClick={addButtonClick}>
                        <Addicon />
                    </IconButton>
                </Tooltip>
            </Stack>
        </Toolbar>
    );
};

export default SitesToolbar;