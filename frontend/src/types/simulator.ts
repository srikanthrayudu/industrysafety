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
  communicationReliability?: number
  safetyCommunicationReliability?: number
  delayMs: number
  throughputPps?: number
  uptimeSeconds?: number
  mtbfSec?: number
  mttrSec?: number
  esdSuccesses?: number
  esdFailures?: number
  alarmDeliverySuccessRate?: number
  emergencyShutdownSuccessRate?: number
  plantSafetyScore?: number
  sensorAvailability?: number
  hazardDetectionAccuracy?: number
  emergencyResponseTimeSec?: number
  activeHazards?: number
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
  riskScore?: number
  riskLevel?: RiskLevel
  activeHazards?: number
  alarmDeliveryRate?: number
  shutdownSuccessRate?: number
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
  activeSafetyScenario?: string | null
  activeScenarioLabel?: string
  scenarioTicksRemaining?: number
  shutdownActive?: boolean
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

export type RiskLevel = 'GREEN' | 'YELLOW' | 'ORANGE' | 'RED' | 'BLACK'

export type ProjectInfo = {
  name: string
  focus: string
  communicationRole: string
}

export type PlantProfile = {
  name: string
  processArea: string
  mode: string
  activeScenario: string
  description: string
}

export type SensorReading = {
  id: string
  label: string
  domain: string
  value: number
  unit: string
  status: 'online' | 'offline'
  riskLevel: RiskLevel
  normalRange: string
  threshold: string
  min: number
  max: number
}

export type Hazard = {
  id: string
  name: string
  domain: string
  level: RiskLevel
  sensorId: string
  reading: number | string
  unit: string
  threshold: string
  description: string
  recommendedActions: string[]
  detectedAt: string
}

export type RiskState = {
  level: RiskLevel
  label: string
  score: number
  drivers: string[]
  hazardCount: number
  shutdownRequired: boolean
  color: string
}

export type EmergencyAction = {
  id: string
  name: string
  target: string
  status: string
  priority: RiskLevel
  owner: string
  etaSeconds: number
  reason: string
}

export type EmergencyState = {
  actions: EmergencyAction[]
  shutdownActive: boolean
  lastShutdownStatus: string
  responseMode: string
}

export type CommunicationState = {
  safetyCommunicationReliability: number
  alarmDeliverySuccessRate: number
  emergencyShutdownSuccessRate: number
  averageResponseDelayMs: number
  missedSensorReadings: number
  currentPath: string[]
  backupRouteActive: boolean
  alarmChannelSuppressed: boolean
}

export type SafetyMetrics = {
  overallPlantSafetyScore: number
  hazardDetectionAccuracy: number
  alarmDeliveryRate: number
  emergencyResponseTimeSec: number
  emergencyShutdownSuccessRate: number
  sensorAvailability: number
  communicationReliability: number
  meanTimeBetweenFailuresSec: number
  meanTimeToRecoverySec: number
}

export type ScenarioCatalogItem = {
  id: string
  label: string
  environment: string
  description: string
}

export type NetworkState = {
  project?: ProjectInfo
  plant?: PlantProfile
  sensors?: SensorReading[]
  hazards?: Hazard[]
  risk?: RiskState
  emergency?: EmergencyState
  communication?: CommunicationState
  safetyMetrics?: SafetyMetrics
  scenarioCatalog?: ScenarioCatalogItem[]
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
