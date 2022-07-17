import * as React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Modal from '@mui/material/Modal';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import SaveIcon from '@mui/icons-material/Save';
import AddIcon from '@mui/icons-material/Add';
import NoItemIcon from '@mui/icons-material/Block';
import Chip from '@mui/material/Chip';
import { blue, red, green } from '@mui/material/colors';
import axios from 'axios';
import { WebsiteRecord, fromPeriodicityString, toPeriodicityString } from './Common';

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

export interface EditSiteModalProps {
    handleClose: (success: boolean) => void;
    record: WebsiteRecord;
}

export default function NewSiteModal(props: EditSiteModalProps) {
    const { handleClose, record } = props;
    const [url, setUrl] = React.useState(record.url);
    const [label, setLabel] = React.useState(record.label);
    const [interval, setInterval] = React.useState(toPeriodicityString(record.interval));
    const [active, setActive] = React.useState(record.active);
    const [regex, setRegex] = React.useState(record.regex);
    const [tags, setTags] = React.useState(record.tags);
    const [newTag, setNewTag] = React.useState('');

    const isEdit = record.pk !== undefined;

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

    const handleActive = (event: React.ChangeEvent<HTMLInputElement>) => {
        setActive(event.target.checked);
    };

    const handleDeleteTag = (index: number) => {
        setTags(tags.filter((_, i) => i !== index));
    }

    const handleNewTag = (event: React.ChangeEvent<HTMLInputElement>) => {
        setNewTag(event.target.value);
    }

    const handleAddTag = () => {
        setTags([...tags, newTag]);
        setNewTag('');
    }

    const handleTagKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            e.preventDefault();
            handleAddTag();
        }
    }

    const handleSave = async () => {
        // verify data are ok
        const inst = axios.create({
            baseURL: 'http://localhost:8000/api/',
            timeout: 10000
        });

        const data = {
            id: record.pk ? record.pk + "" : record.pk,
            url,
            label,
            interval: fromPeriodicityString(interval),
            active,
            regex,
            tags: tags.join(",")
        };

        try {
            if (isEdit) {
                console.log("Updating this: ", JSON.stringify(data));
                const response = await inst.post("record/", data);
                if (response.status > 204) {
                    // show error
                    console.log(response);
                }
            } else {
                console.log("Inserting this: ", JSON.stringify(data));
                const response = await inst.put("record/", data);
                if (response.status > 201) {
                    // show error
                    console.log(response);
                }
            }

            handleClose(true);
        } catch (error) {
            console.error(error);
        }
    }

    return (
        <Modal
            open={true}

            onClose={handleClose}
        >
            <Box sx={style}>
                <Typography id="modal-modal-title" variant="h6" component="h2">
                    {isEdit ? "Update" : "Add a new"} website record
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
                <FormControlLabel control={
                    <Checkbox checked={active} onChange={handleActive} />
                } label="Active" />

                <Typography sx={{ mb: 1, mt: 1 }}>Tags</Typography>
                <Stack direction="row" sx={{ flexWrap: "wrap" }}>
                    {tags.length > 0 ? tags.map((value, index) => (
                        <Chip
                            label={value}
                            variant="outlined"
                            onDelete={() => handleDeleteTag(index)}
                            key={index}
                            sx={{ margin: "2px" }}
                        />
                    )) :
                        <Chip icon={<NoItemIcon />} label="No tags were added" key={0} />

                    }
                </Stack>
                <Stack direction="row" spacing={2} justifyContent="space-between" alignItems={"center"} >
                    <TextField
                        id="tag"
                        label="Add a new tag"
                        sx={{ ...textFieldStyle, flexGrow: 1 }}
                        value={newTag}
                        onChange={handleNewTag}
                        onKeyPress={handleTagKeyPress}
                    />
                    <Button
                        variant="outlined"
                        sx={{ color: green[500], width: 120, borderColor: green[500] }}
                        startIcon={<AddIcon />}
                        onClick={handleAddTag}
                    >
                        Add tag
                    </Button>
                </Stack>
                <Stack direction="row" spacing={2} justifyContent="flex-end">
                    <Button variant="contained" sx={{ backgroundColor: blue[500] }} startIcon={<SaveIcon />} onClick={handleSave}>Save</Button>
                    <Button variant="contained" sx={{ backgroundColor: red[500] }} onClick={() => handleClose(false)}>Cancel</Button>
                </Stack>
            </Box>
        </Modal>
    );
}
