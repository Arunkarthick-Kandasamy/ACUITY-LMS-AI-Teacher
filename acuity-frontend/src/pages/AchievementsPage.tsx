import { useState, useEffect } from 'react';
import { apiRequest } from '../services/api';

interface Achievement {
  id: string;
  badge_name: string;
  badge_icon_url: string | null;
  badge_category: string;
  earned_at: string;
}

interface Streak {
  current_streak: number;
  longest_streak: number;
}

const AchievementsPage = () => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [streak, setStreak] = useState<Streak | null>(null);

  useEffect(() => {
    apiRequest('/gamification/achievements/me').then((res: any) => setAchievements(res?.data || [])).catch(() => {});
    apiRequest('/gamification/streak/me').then((res: any) => setStreak(res?.data || null)).catch(() => {});
  }, []);

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Achievements</h1>
      {streak && (
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-lg p-6 mb-6 text-center">
          <div className="text-4xl font-bold text-amber-600">{streak.current_streak}</div>
          <div className="text-sm text-amber-700">Day Streak</div>
          <div className="text-xs text-amber-500 mt-1">Longest: {streak.longest_streak} days</div>
        </div>
      )}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {achievements.map((a) => (
          <div key={a.id} className="bg-white p-4 rounded-lg border text-center hover:shadow-md transition-shadow">
            <div className="text-4xl mb-2">{a.badge_icon_url || '🏆'}</div>
            <div className="font-medium">{a.badge_name}</div>
            <div className="text-xs text-gray-500 mt-1">{a.badge_category}</div>
            <div className="text-xs text-gray-400 mt-1">{new Date(a.earned_at).toLocaleDateString()}</div>
          </div>
        ))}
      </div>
      {achievements.length === 0 && <p className="text-gray-500 text-center py-12">No achievements yet. Keep learning!</p>}
    </div>
  );
};

export default AchievementsPage;
