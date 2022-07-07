import * as React from 'react';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import { alpha } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import Tooltip from '@mui/material/Tooltip';
import Stack from '@mui/material/Stack';
import DeleteIcon from '@mui/icons-material/Delete';
import Addicon from '@mui/icons-material/Add';
import FilterListIcon from '@mui/icons-material/FilterList';

export interface SitesToolbarProps {
    numSelected: number;
    toggleFilterList: React.Dispatch<React.SetStateAction<boolean>>;
    addButtonClick: () => void;
    deleteButtonClick: () => void;
}

const SitesToolbar = (props: SitesToolbarProps) => {
    const { numSelected, toggleFilterList, addButtonClick, deleteButtonClick } = props;
    const [filterListShown, setFilterListShown] = React.useState(false);

    return (
        <Toolbar
            sx={{
                pl: { sm: 2 },
                pr: { xs: 1, sm: 1 },
                ...(numSelected > 0 && {
                    bgcolor: (theme) =>
                        alpha(theme.palette.primary.main, theme.palette.action.activatedOpacity),
                }),
            }}
        >
            {numSelected > 0 ? (
                <Typography
                    sx={{ flex: '1 1 100%' }}
                    color="inherit"
                    variant="subtitle1"
                    component="div"
                >
                    {numSelected} selected
                </Typography>
            ) : (
                <Typography
                    sx={{ flex: '1 1 100%' }}
                    variant="h6"
                    id="tableTitle"
                    component="h1"
                    color="primary"
                >
                    Sites
                </Typography>
            )}
            <Stack direction="row" spacing={2}>
                {numSelected === 0 ? (
                    <React.Fragment>
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
                    </React.Fragment>
                ) :
                    <Tooltip title="Delete">
                        <IconButton onClick={deleteButtonClick}>
                            <DeleteIcon />
                        </IconButton>
                    </Tooltip>
                }
            </Stack>
        </Toolbar>
    );
};

export default SitesToolbar;