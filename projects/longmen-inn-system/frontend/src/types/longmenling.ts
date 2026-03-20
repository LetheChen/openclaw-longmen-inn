// 龙门令记录类型
export enum LongmenlingType {
  TASK_COMPLETED = 'task_completed',
  PROJECT_COMPLETED = 'project_completed',
  DAILY_LOGIN = 'daily_login',
  ACHIEVEMENT = 'achievement',
  BONUS = 'bonus',
  PENALTY = 'penalty',
}

// 等级定义
export interface Level {
  level: number;
  title: string;
  minPoints: number;
  maxPoints: number;
  icon?: string;
  color?: string;
}

// 龙门令记录
export interface LongmenlingRecord {
  id: string;
  agentId: string;
  agentName: string;
  agentAvatar?: string;
  type: LongmenlingType;
  points: number;
  reason: string;
  relatedTaskId?: string;
  relatedTaskTitle?: string;
  relatedProjectId?: string;
  relatedProjectName?: string;
  metadata?: Record<string, any>;
  createdAt: string;
}

// 排行榜项
export interface RankingItem {
  rank: number;
  agentId: string;
  agentName: string;
  agentAvatar?: string;
  agentTitle?: string;
  level: number;
  totalPoints: number;
  monthlyPoints: number;
  weeklyPoints: number;
  completedTasks: number;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: number;
}

// 排行榜统计
export interface RankingStatistics {
  totalAgents: number;
  activeAgents: number;
  totalPointsDistributed: number;
  topPerformerId?: string;
  topPerformerName?: string;
}

// 趋势数据点
export interface TrendDataPoint {
  date: string;
  points: number;
  taskCount: number;
}

// 个人趋势
export interface PersonalTrend {
  agentId: string;
  agentName: string;
  dailyTrend: TrendDataPoint[];
  weeklyTrend: TrendDataPoint[];
  monthlyTrend: TrendDataPoint[];
}

// 成就/徽章
export interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  condition: string;
  pointsBonus: number;
}

// 用户成就
export interface UserBadge {
  badgeId: string;
  badgeName: string;
  badgeIcon: string;
  badgeColor: string;
  earnedAt: string;
}

// 等级配置
export const LEVEL_CONFIG: Level[] = [
  { level: 1, title: '店小二', minPoints: 0, maxPoints: 100, color: '#8B4513' },
  { level: 2, title: '跑腿伙计', minPoints: 100, maxPoints: 300, color: '#2E8B57' },
  { level: 3, title: '账房先生', minPoints: 300, maxPoints: 600, color: '#4682B4' },
  { level: 4, title: '掌柜助理', minPoints: 600, maxPoints: 1000, color: '#9370DB' },
  { level: 5, title: '二掌柜', minPoints: 1000, maxPoints: 1500, color: '#DC143C' },
  { level: 6, title: '大掌柜', minPoints: 1500, maxPoints: 2200, color: '#B8860B' },
  { level: 7, title: '龙门使者', minPoints: 2200, maxPoints: 3000, color: '#8B0000' },
  { level: 8, title: '江湖传奇', minPoints: 3000, maxPoints: 4000, color: '#FFD700' },
  { level: 9, title: '武林盟主', minPoints: 4000, maxPoints: 5500, color: '#FF6347' },
  { level: 10, title: '一代宗师', minPoints: 5500, maxPoints: 999999, color: '#8B008B' },
];

// 根据龙门令数获取等级信息
export function getLevelByPoints(points: number): Level {
  return LEVEL_CONFIG.find(level => points >= level.minPoints && points < level.maxPoints) || LEVEL_CONFIG[0];
}

// 获取下一等级信息
export function getNextLevel(points: number): Level | null {
  const currentLevel = getLevelByPoints(points);
  const nextLevelIndex = LEVEL_CONFIG.findIndex(l => l.level === currentLevel.level) + 1;
  return nextLevelIndex < LEVEL_CONFIG.length ? LEVEL_CONFIG[nextLevelIndex] : null;
}

// 获取升级进度百分比
export function getLevelProgress(points: number): number {
  const currentLevel = getLevelByPoints(points);
  const nextLevel = getNextLevel(points);
  
  if (!nextLevel) return 100;
  
  const range = nextLevel.minPoints - currentLevel.minPoints;
  const progress = points - currentLevel.minPoints;
  return Math.round((progress / range) * 100);
}
