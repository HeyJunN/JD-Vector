/**
 * useRoadmapProgress Hook - 로드맵 진행률 로컬 스토리지 관리
 *
 * 사용자가 체크한 태스크를 로컬 스토리지에 저장하여
 * 새로고침 후에도 진행률이 유지되도록 함
 */

import { useState, useEffect } from 'react';
import type { RoadmapWeek } from '../types/roadmap.types';

const STORAGE_KEY_PREFIX = 'jd-vector-roadmap-progress';

export const useRoadmapProgress = (
  roadmapId: string,
  initialWeeks: RoadmapWeek[]
) => {
  const storageKey = `${STORAGE_KEY_PREFIX}-${roadmapId}`;

  // 로컬 스토리지에서 진행률 불러오기
  const loadProgress = (): Set<string> => {
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        const data = JSON.parse(saved);
        return new Set(data);
      }
    } catch (error) {
      console.error('Failed to load roadmap progress:', error);
    }
    return new Set();
  };

  // 진행률 저장
  const saveProgress = (completedTasks: Set<string>) => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(Array.from(completedTasks)));
    } catch (error) {
      console.error('Failed to save roadmap progress:', error);
    }
  };

  // 완료된 태스크 ID 집합 (week_number-task_index 형태)
  const [completedTaskIds, setCompletedTaskIds] = useState<Set<string>>(loadProgress);

  // 초기 로드 시 저장된 진행률 적용
  const [weeklyPlan, setWeeklyPlan] = useState<RoadmapWeek[]>(() => {
    const savedIds = loadProgress();
    return initialWeeks.map((week) => ({
      ...week,
      tasks: week.tasks.map((task, index) => {
        const taskId = `${week.week_number}-${index}`;
        return {
          ...task,
          completed: savedIds.has(taskId) || task.completed,
        };
      }),
    }));
  });

  // 태스크 토글 핸들러
  const toggleTask = (weekNumber: number, taskIndex: number) => {
    const taskId = `${weekNumber}-${taskIndex}`;

    setWeeklyPlan((prev) =>
      prev.map((week) =>
        week.week_number === weekNumber
          ? {
              ...week,
              tasks: week.tasks.map((task, index) =>
                index === taskIndex
                  ? { ...task, completed: !task.completed }
                  : task
              ),
            }
          : week
      )
    );

    setCompletedTaskIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(taskId)) {
        newSet.delete(taskId);
      } else {
        newSet.add(taskId);
      }
      saveProgress(newSet);
      return newSet;
    });
  };

  // 진행률 초기화
  const resetProgress = () => {
    setCompletedTaskIds(new Set());
    localStorage.removeItem(storageKey);
    setWeeklyPlan(initialWeeks);
  };

  // 모든 태스크 완료 여부
  const isAllCompleted = weeklyPlan.every((week) =>
    week.tasks.every((task) => task.completed)
  );

  return {
    weeklyPlan,
    toggleTask,
    resetProgress,
    isAllCompleted,
  };
};

export default useRoadmapProgress;
