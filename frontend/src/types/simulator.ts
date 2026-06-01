export type NodeStatus = 'active' | 'failed'

export type NetworkNode = {
  id: string
  label: string
  role: string
  status: NodeStatus
  reading?: number | null
  unit?: string
  fail_count?: number
  repair_count?: number
  uptime_seconds?: number
  downtime_seconds?: number
}

export type NetworkLink = {
  id?: string
  source: string
  target: string
  active: boolean
  latency_ms?: number
  loss_rate?: number
  protocol?: string
}

export type Metrics = {
  packetsSent: number
  packetsReceived: number
  packetsLost: number
  packetLossPercent: number
  reliability: number
  delayMs: number
  throughputPps?: number
  uptimeSeconds?: number
  mtbfSec?: number
  mttrSec?: number
  esdSuccesses?: number
  esdFailures?: number
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
  throughputPps?: number
}

export type RouteInfo = {
  monitoredFlow: { from: string; to: string }
  primary: string[]
  current: string[]
  backupActive: boolean
}

export type ScenarioState = {
  alarmSuppressed: boolean
  falseDataActive: boolean
  dosActive: boolean
}

export type SafetyStatus = {
  level: 'normal' | 'degraded' | 'critical'
  violations: string[]
  thresholdsMet: boolean
}

export type SafetyThresholds = {
  minReliability: number
  maxDelayMs: number
  maxPacketLossPercent: number
}

export type NetworkState = {
  nodes: NetworkNode[]
  links: NetworkLink[]
  metrics: Metrics
  routes: RouteInfo
  scenario?: ScenarioState
  safety?: SafetyStatus
  thresholds?: SafetyThresholds
  alerts: Alert[]
  logs: LogEntry[]
  history: HistoryEntry[]
}
