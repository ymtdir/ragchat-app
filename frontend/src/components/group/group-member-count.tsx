/**
 * グループメンバー数表示コンポーネント
 *
 * グループのメンバー数を表示します。
 */

import { useEffect, useState } from "react";
import { Users } from "lucide-react";
import { MembershipService } from "@/services/membership-service";
import { Badge } from "@/components/ui/badge";

interface GroupMemberCountProps {
  groupId: number;
  className?: string;
}

export function GroupMemberCount({ groupId, className }: GroupMemberCountProps) {
  const [memberCount, setMemberCount] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMemberCount = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const count = await MembershipService.getGroupMemberCount(groupId);
        setMemberCount(count);
      } catch (err) {
        console.error("メンバー数の取得に失敗:", err);
        setError("メンバー数の取得に失敗しました");
        setMemberCount(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMemberCount();
  }, [groupId]);

  if (isLoading) {
    return (
      <div className={`flex items-center gap-1 ${className}`}>
        <Users className="h-4 w-4 text-muted-foreground" />
        <div className="h-5 w-8 animate-pulse rounded bg-muted"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex items-center gap-1 text-muted-foreground ${className}`}>
        <Users className="h-4 w-4" />
        <span className="text-sm">-</span>
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-1 ${className}`}>
      <Users className="h-4 w-4 text-muted-foreground" />
      <Badge variant="secondary" className="text-xs">
        {memberCount}
      </Badge>
    </div>
  );
}