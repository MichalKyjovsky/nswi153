import * as React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Modal from '@mui/material/Modal';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import SaveIcon from '@mui/icons-material/Save';
import { blue, red } from '@mui/material/colors';
import { WebsiteRecord } from './Common';

const style = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 600,
    bgcolor: 'background.paper',
    border: '2px solid #000',
    boxShadow: 24,
    p: 4,
};

const textFieldStyle = {
    mt: 2,
    mb: 2
};

const periodicityRegex = /^((\d+)d)?((\d+)h)?((\d+)m)?$/g;

const toPeriodicityString = (period: number): string => {
    let remaining = period;
    const days = remaining / 1440;
    remaining %= 1440;
    const hours = remaining / 60;
    const minutes = remaining % 60;
    return `${days}d ${hours}h ${minutes}m`;
};

const fromPeriodicityString = (periodicity: string): number | null => {
    const match = periodicityRegex.exec(periodicity.replace(/\s/g, ''));
    if (match && (match[2] || match[4] || match[6])) {
        let period: number = 0;
        if (match[2]) {
            period += Number(match[2]) * 1440;
        }
        if (match[4]) {
            period += Number(match[4]) * 60;
        }
        if (match[6]) {
            period += Number(match[6]);
        }
        return period;
    }
    return null;
};

export interface EditSiteModalProps {
    handleClose: () => void;
    record: WebsiteRecord;
}

export default function NewSiteModal(props: EditSiteModalProps) {
    const { handleClose, record } = props;
    const [url, setUrl] = React.useState(record.url);
    const [label, setLabel] = React.useState(record.label);
    const [interval, setInterval] = React.useState(toPeriodicityString(record.interval));
    const [actvie, setActive] = React.useState(record.active);
    const [regex, setRegex] = React.useState(record.regex);
    const [tags, setTags] = React.useState(record.tags);

    const handleUrl = (event: React.ChangeEvent<HTMLInputElement>) => {
        setUrl(event.target.value);
    }

    const handleRegex = (event: React.ChangeEvent<HTMLInputElement>) => {
        setRegex(event.target.value);
    }

    const handleLabel = (event: React.ChangeEvent<HTMLInputElement>) => {
        setLabel(event.target.value);
    }

    const handleInterval = (event: React.ChangeEvent<HTMLInputElement>) => {
        setInterval(event.target.value);
    }

    return (
        <div>
            <Modal
                open={true}

                onClose={handleClose}
            >
                <Box sx={style}>
                    <Typography id="modal-modal-title" variant="h6" component="h2">
                        {record.pk ? "Update" : "Add a new"} website record
                    </Typography>
                    <TextField
                        required
                        id="url"
                        label="URL"
                        placeholder="URL where the crawler should start"
                        fullWidth
                        sx={textFieldStyle}
                        value={url}
                        onChange={handleUrl}
                    />
                    <TextField
                        required
                        id="label"
                        label="Label"
                        placeholder="Displayed label for this record"
                        fullWidth
                        sx={textFieldStyle}
                        value={label}
                        onChange={handleLabel}
                    />
                    <TextField
                        required
                        id="regex"
                        label="Boundary RegExp"
                        placeholder="Found links must match this expression to be followed"
                        fullWidth
                        sx={textFieldStyle}
                        value={regex}
                        onChange={handleRegex}
                    />
                    <TextField
                        required
                        id="periodicity"
                        label="Periodicity"
                        placeholder="Format: %d %h %m (e.g. '1d 2h 30m', '6h', '2h 30m')"
                        fullWidth
                        sx={textFieldStyle}
                        value={interval}
                        onChange={handleInterval}
                    />
                    <Stack direction="row" spacing={2} justifyContent="flex-end">
                        <Button variant="contained" sx={{ backgroundColor: blue[500] }} startIcon={<SaveIcon />}>Save</Button>
                        <Button variant="contained" sx={{ backgroundColor: red[500] }}>Cancel</Button>
                    </Stack>
                </Box>
            </Modal>
        </div>
    );
}
