export type NodeStatus = 'active' | 'failed'

export type NetworkNode = {
  id: string
  label: string
  role: string
  status: NodeStatus
}

export type NetworkLink = {
  source: string
  target: string
  active: boolean
}

export type Metrics = {
  packetsSent: number
  packetsReceived: number
  packetsLost: number
  packetLossPercent: number
  reliability: number
  delayMs: number
  activeNodes: number
  failedNodes: number
}

export type Alert = {
  time: string
  level: 'warning' | 'critical' | 'success'
  message: string
}

export type LogEntry = {
  time: string
  event: string
}

export type HistoryEntry = {
  time: string
  reliability: number
  packetLossPercent: number
  delayMs: number
}

export type RouteInfo = {
  monitoredFlow: { from: string; to: string }
  primary: string[]
  current: string[]
  backupActive: boolean
}

export type NetworkState = {
  nodes: NetworkNode[]
  links: NetworkLink[]
  metrics: Metrics
  routes: RouteInfo
  alerts: Alert[]
  logs: LogEntry[]
  history: HistoryEntry[]
}
