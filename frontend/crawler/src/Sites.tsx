import * as React from 'react';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableFooter from '@mui/material/TableFooter';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import TablePaginationActions from './TablePaginationActions';
import Checkbox from '@mui/material/Checkbox';
import Chip from '@mui/material/Chip';
import IconButton from '@mui/material/IconButton';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import SitesToolbar from './SitesToolbar';
import NewSiteModal from './EditSiteModal';
import { WebsiteRecord, emptyWebsiteRecord, WebsiteRecordForView, Order } from './Common';
import ApiManager from './ApiManager';
import SitesTableHead from './SitesTableHead';

function SitesContent() {
    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(10);
    const [filterListShown, setFilterListShown] = React.useState(false);
    const [rows, setRows] = React.useState<WebsiteRecordForView[]>([]);
    const [totalRecords, setTotalRecords] = React.useState(0);
    const [editModalOpen, setEditModalOpen] = React.useState(false);
    const [editedRecord, setEditedRecord] = React.useState<WebsiteRecord>(emptyWebsiteRecord());
    const [confirmDeleteOpen, setConfirmDeleteOpen] = React.useState(false);
    const [deletedRecord, setDeletedRecord] = React.useState(0);
    const [labelFilter, setLabelFilter] = React.useState("");
    const [urlFilter, setUrlFilter] = React.useState("");
    const [tagsFilter, setTagsFilter] = React.useState("");
    const [order, setOrder] = React.useState<Order>('asc');
    const [orderBy, setOrderBy] = React.useState<keyof WebsiteRecordForView>('label');

    const manager = React.useMemo(() => new ApiManager(), []);
    const getRows = React.useCallback(async (pageSize: number, pageNumber: number, lblFilter: string, tags: string, url: string, sortOrder: Order, sortProperty: keyof WebsiteRecordForView) => {
        const response = await manager.getRecordPage(pageSize, pageNumber, lblFilter, tags, url, sortOrder, sortProperty);
        setRows(response ? response.records : []);
        response && setTotalRecords(response.totalRecords);
    }, [manager]);

    React.useEffect(() => {
        getRows(rowsPerPage, page, labelFilter, tagsFilter, urlFilter, order, orderBy);
    }, [page, rowsPerPage, labelFilter, tagsFilter, urlFilter, order, orderBy, getRows]);

    // Avoid a layout jump when reaching the last page with empty rows.
    const emptyRows = totalRecords > rowsPerPage ? rowsPerPage - rows.length : 0;

    const handleChangePage = (event: React.MouseEvent<HTMLButtonElement> | null, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const handleRequestSort = (
        event: React.MouseEvent<unknown>,
        property: keyof WebsiteRecordForView,
    ) => {
        const isAsc = orderBy === property && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(property);
    };

    const handleRequestFilter = (
        property: keyof WebsiteRecordForView,
        value: string
    ) => {
        if (property === "label") {
            setLabelFilter(value);
        } else if (property === "tags") {
            setTagsFilter(value);
        } else if (property === "url") {
            setUrlFilter(value);
        }
    };

    const handleCloseEditModal = (success: boolean) => {
        setEditModalOpen(false);
        if (success) {
            getRows(rowsPerPage, page, labelFilter, tagsFilter, urlFilter, order, orderBy);
        }
    }
    const handleAddRecordClick = () => {
        setEditedRecord(emptyWebsiteRecord());
        setEditModalOpen(true);
    }
    const handleEditRecordClick = async (id: number) => {
        const record = await manager.getRecord(id);
        if (record) {
            setEditedRecord(record);
            setEditModalOpen(true);
        }
    }

    const handleRecordDeleteClick = (id: number) => {
        setDeletedRecord(id);
        setConfirmDeleteOpen(true);
    };

    const handleRecordDeleteClose = async (shouldDelete: boolean) => {
        setConfirmDeleteOpen(false);
        if (shouldDelete) {
            try {
                await manager.deleteRecord(deletedRecord);
            } catch (error) {
                console.log(error);
            }
            getRows(rowsPerPage, page, labelFilter, tagsFilter, urlFilter, order, orderBy);
        }
    };

    return (
        <Box sx={{ display: 'flex' }}>
            <Box
                component="main"
                sx={{
                    backgroundColor: (theme) => theme.palette.grey[100],
                    flexGrow: 1,
                    //height: '100vh',
                    overflow: 'auto',
                }}
            >
                <Container maxWidth={false} sx={{ mt: 2, mb: 2, minWidth: 800, maxWidth: 1600 }}>
                    <SitesToolbar toggleFilterList={setFilterListShown} addButtonClick={handleAddRecordClick} />
                    <TableContainer component={Paper} >
                        {editModalOpen && <NewSiteModal handleClose={handleCloseEditModal} record={editedRecord} />}
                        {confirmDeleteOpen && (
                            <Dialog
                                open={true}
                                onClose={() => handleRecordDeleteClose(false)}
                            >
                                <DialogTitle>{"Confirm delete"}</DialogTitle>
                                <DialogContent>
                                    <DialogContentText>
                                        Are you sure you want to delete this website record?
                                    </DialogContentText>
                                </DialogContent>
                                <DialogActions>
                                    <Button onClick={() => handleRecordDeleteClose(true)}>Delete</Button>
                                    <Button onClick={() => handleRecordDeleteClose(false)} autoFocus>
                                        Cancel
                                    </Button>
                                </DialogActions>
                            </Dialog>)
                        }
                        <Table sx={{ minWidth: 500 }} size={'small'}>
                            <SitesTableHead
                                order={order}
                                orderBy={orderBy}
                                onRequestSort={handleRequestSort}
                                onRequestFilter={handleRequestFilter}
                                filterListShown={filterListShown}
                            />
                            <TableBody>
                                {rows.map((row: WebsiteRecordForView, index: number) => {
                                    return (
                                        <TableRow
                                            hover
                                            tabIndex={-1}
                                            key={row.label}
                                        >
                                            <TableCell>{row.label}</TableCell>
                                            <TableCell>{row.url}</TableCell>
                                            <TableCell>{row.periodicity}</TableCell>
                                            <TableCell><Checkbox checked={row.active} /></TableCell>
                                            <TableCell>
                                                {
                                                    row.tags.map((tag: string, tagIndex: number) =>
                                                        <Chip
                                                            sx={{ ml: "1px", mr: "1px" }}
                                                            label={tag}
                                                            variant="outlined"
                                                            key={`itm-${index}-tag-${tagIndex}`}
                                                        />
                                                    )
                                                }
                                            </TableCell>
                                            <TableCell>{row.last_crawl}</TableCell>
                                            <TableCell>{row.lastExecutionStatus}</TableCell>
                                            <TableCell>
                                                <IconButton onClick={() => handleEditRecordClick(row.pk)}><EditIcon /></IconButton>
                                                <IconButton onClick={() => handleRecordDeleteClick(row.pk)}><DeleteIcon /></IconButton>
                                            </TableCell>
                                        </TableRow>
                                    );
                                })}
                                {emptyRows > 0 && (
                                    <TableRow
                                        style={{
                                            height: 55 * emptyRows,
                                        }}
                                    >
                                        <TableCell colSpan={6} />
                                    </TableRow>
                                )}
                            </TableBody>
                            <TableFooter>
                                <TableRow>
                                    <TablePagination
                                        rowsPerPageOptions={[5, 10, 25]}
                                        colSpan={6}
                                        count={totalRecords}
                                        rowsPerPage={rowsPerPage}
                                        page={page}
                                        onPageChange={handleChangePage}
                                        onRowsPerPageChange={handleChangeRowsPerPage}
                                        ActionsComponent={TablePaginationActions}
                                    />
                                </TableRow>
                            </TableFooter>
                        </Table>
                    </TableContainer>
                </Container>
            </Box>
        </Box>
    );
}

export default function Sites() {
    return <SitesContent />;
}
