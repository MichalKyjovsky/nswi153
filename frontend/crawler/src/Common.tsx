export interface WebsiteRecord {
    pk?: number,
    url: string,
    label: string,
    interval: number,
    active: boolean,
    regex: string,
    tags: string[]
}

export function createWebsiteRecord(
    url: string,
    label: string,
    interval: number,
    active: boolean,
    regex: string,
    tags: string[],
    pk?: number
): WebsiteRecord {
    return {
        pk,
        url,
        label,
        interval,
        active,
        regex,
        tags
    };
}

export function emptyWebsiteRecord(): WebsiteRecord {
    return {
        url: "",
        label: "",
        interval: 0,
        active: false,
        regex: "",
        tags: []
    };
}

export interface WebsiteRecordForView {
    pk: number,
    url: string,
    label: string,
    interval: number,
    active: boolean,
    regex: string,
    tags: string[]
}