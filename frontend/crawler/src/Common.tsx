export const API_BASE_URL = 'http://localhost:8000/api/';

export type Order = 'asc' | 'desc';

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
    periodicity: string,
    active: boolean,
    tags: string[],
    last_crawl: string,
    lastExecutionStatus: string,
    actions: boolean
}

export function createWebsiteRecordForView(
    pk: number,
    url: string,
    label: string,
    periodicity: string,
    active: boolean,
    tags: string[],
    lastExecutionTime: string,
    lastExecutionStatus: string
): WebsiteRecordForView {
    return {
        pk,
        url,
        label,
        periodicity,
        active,
        tags,
        last_crawl: lastExecutionTime,
        lastExecutionStatus,
        actions: true
    };
}

export interface ExecutionRecord {
    pk: number,
    websiteRecordLabel: string,
    websiteRecordPk: number,
    status: string,
    lastExecutionTime: string,
    lastExecutionDuration: number,
    sitesCrawled: number,
    actions: boolean
}

export function createExecutionRecord(
    pk: number,
    websiteRecordLabel: string,
    websiteRecordPk: number,
    status: string,
    lastExecutionTime: string,
    lastExecutionDuration: number,
    sitesCrawled: number
): ExecutionRecord {
    return {
        pk,
        websiteRecordLabel,
        websiteRecordPk,
        status,
        lastExecutionTime,
        lastExecutionDuration,
        sitesCrawled,
        actions: true
    };
}

export interface LayoutNode {
    id: string;
    layoutPosX: number;
    layoutPosY: number;
    layoutForceX: number;
    layoutForceY: number;
    data: {
        crawlTime: string,
        url: string,
        owner: number
    }
}

export function createLayoutNode(id: string, crawlTime: string, url: string, owner: number): LayoutNode {
    return {
        id,
        layoutPosX: 0,
        layoutPosY: 0,
        layoutForceX: 0,
        layoutForceY: 0,
        data: {
            crawlTime,
            url,
            owner
        }
    };
}

export interface LayoutEdge {
    source: LayoutNode,
    target: LayoutNode,
    weight: number
}

export function createLayoutEdge(source: LayoutNode, target: LayoutNode): LayoutEdge {
    return {
        source,
        target,
        weight: 1
    };
}

export interface LayoutGraph {
    nodes: LayoutNode[];
    edges: LayoutEdge[];
    layoutMinX: number;
    layoutMaxX: number;
    layoutMinY: number;
    layoutMaxY: number;
}

export function createLayoutGraph(nodes: LayoutNode[], edges: LayoutEdge[]): LayoutGraph {
    return {
        nodes,
        edges,
        layoutMinX: 0,
        layoutMaxX: 0,
        layoutMinY: 0,
        layoutMaxY: 0
    };
}

const periodicityRegex = /^((\d+)d)?((\d+)h)?((\d+)m)?((\d+)s)?$/;

export function toPeriodicityString(period: number): string {
    let remaining = period;
    const days = (remaining / 86400) >> 0;
    remaining %= 86400;
    const hours = (remaining / 3600) >> 0;
    remaining %= 3600;
    const minutes = (remaining / 60) >> 0;
    const seconds = remaining % 60;
    const result = (days > 0 ? `${days}d ` : "")
        + (hours > 0 ? `${hours}h ` : "")
        + (minutes > 0 ? `${minutes}m ` : "")
        + (seconds > 0 ? `${seconds}s` : "");

    return result !== "" ? result.trim() : "0s";
};

export function fromPeriodicityString(periodicity: string): number | null {
    const match = periodicityRegex.exec(periodicity.replace(/\s/g, ''));
    if (match && (match[2] || match[4] || match[6] || match[8])) {
        let period: number = 0;
        if (match[2]) {
            period += Number(match[2]) * 86400;
        }
        if (match[4]) {
            period += Number(match[4]) * 3600;
        }
        if (match[6]) {
            period += Number(match[6]) * 60;
        }
        if (match[8]) {
            period += Number(match[8]);
        }
        return period;
    }
    return null;
};