/**
 * メンバーシップサービス
 *
 * グループのメンバー管理に関するAPI呼び出しを提供します。
 */

import type {
  MembersResponse,
  UserMembershipsResponse,
  MembershipCreate,
  Membership,
  BulkMembershipCreate,
  BulkMembershipResponse,
  BulkMembershipDelete,
  BulkMembershipDeleteResponse,
  MemberDeleteResponse,
  User,
} from "@/types/api";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

class MembershipServiceClass {
  /**
   * 認証トークンを取得
   */
  private getAuthToken(): string {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("認証トークンが見つかりません。ログインしてください。");
    }
    return token;
  }

  /**
   * 認証ヘッダーを含むリクエストヘッダーを取得
   */
  private getAuthHeaders(): HeadersInit {
    return {
      "Content-Type": "application/json",
      Authorization: `Bearer ${this.getAuthToken()}`,
    };
  }

  /**
   * レスポンスのエラーハンドリング
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    console.log(
      `API Response: ${response.status} ${response.statusText} for ${response.url}`
    );

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `HTTPエラー: ${response.status}`;

      try {
        const errorData = JSON.parse(errorText);
        errorMessage = errorData.detail || errorMessage;
        console.error("API Error Details:", errorData);
      } catch {
        errorMessage = errorText || errorMessage;
        console.error("API Error Text:", errorText);
      }

      throw new Error(errorMessage);
    }

    const data = await response.json();
    console.log("API Response Data:", data);
    return data;
  }

  /**
   * グループのメンバー一覧を取得
   */
  async getGroupMembers(
    groupId: number,
    includeDeleted = false
  ): Promise<MembersResponse> {
    const url = `${API_BASE_URL}/api/memberships/groups/${groupId}/members?include_deleted=${includeDeleted}`;

    const response = await fetch(url, {
      method: "GET",
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse<MembersResponse>(response);
  }

  /**
   * ユーザーの所属グループ一覧を取得
   */
  async getUserMemberships(
    userId: number,
    includeDeleted = false
  ): Promise<UserMembershipsResponse> {
    const url = `${API_BASE_URL}/api/memberships/users/${userId}/groups?include_deleted=${includeDeleted}`;

    const response = await fetch(url, {
      method: "GET",
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse<UserMembershipsResponse>(response);
  }

  /**
   * グループにメンバーを追加
   */
  async addMemberToGroup(membership: MembershipCreate): Promise<Membership> {
    const response = await fetch(`${API_BASE_URL}/api/memberships/`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(membership),
    });

    return this.handleResponse<Membership>(response);
  }

  /**
   * グループからメンバーを削除
   */
  async removeMemberFromGroup(
    groupId: number,
    userId: number
  ): Promise<MemberDeleteResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/memberships/groups/${groupId}/users/${userId}`,
      {
        method: "DELETE",
        headers: this.getAuthHeaders(),
      }
    );

    return this.handleResponse<MemberDeleteResponse>(response);
  }

  /**
   * グループに複数のメンバーを一括追加
   */
  async addMultipleMembersToGroup(
    bulkMembership: BulkMembershipCreate
  ): Promise<BulkMembershipResponse> {
    const response = await fetch(`${API_BASE_URL}/api/memberships/bulk-add`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(bulkMembership),
    });

    return this.handleResponse<BulkMembershipResponse>(response);
  }

  /**
   * グループから複数のメンバーを一括削除
   */
  async removeMultipleMembersFromGroup(
    bulkMembership: BulkMembershipDelete
  ): Promise<BulkMembershipDeleteResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/memberships/bulk-remove`,
      {
        method: "POST",
        headers: this.getAuthHeaders(),
        body: JSON.stringify(bulkMembership),
      }
    );

    return this.handleResponse<BulkMembershipDeleteResponse>(response);
  }

  /**
   * 利用可能なユーザー一覧を取得（メンバー追加用）
   *
   * 注: これは既存のuser-serviceを使用します
   */
  async getAvailableUsers(): Promise<User[]> {
    const response = await fetch(`${API_BASE_URL}/api/users/`, {
      method: "GET",
      headers: this.getAuthHeaders(),
    });

    const data = await this.handleResponse<{ users: User[] }>(response);
    return data.users;
  }

  /**
   * グループのメンバー数を取得
   */
  async getGroupMemberCount(groupId: number): Promise<number> {
    const membersResponse = await this.getGroupMembers(groupId, false);
    return membersResponse.total_count;
  }
}

export const MembershipService = new MembershipServiceClass();
