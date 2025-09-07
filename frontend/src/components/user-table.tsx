/* eslint-disable react-refresh/only-export-components */
"use client";

import * as React from "react";
import { flexRender } from "@tanstack/react-table";
import type { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown, ChevronDown, MoreHorizontal } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useUserTable } from "@/hooks/use-user-table";
import { UserEditModal } from "./user-edit-modal";
import { UserDeleteDialog } from "./user-delete-dialog";
import { UserBulkDeleteDialog } from "./user-bulk-delete-dialog";
import type { User } from "@/types/api";

// columnsの定義を関数内に移動するため、ここでは型のみ定義
export const createColumns = (
  handleEditUser: (user: User) => void,
  handleDeleteUser: (user: User) => void
): ColumnDef<User>[] => [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && "indeterminate")
        }
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="全選択"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="行選択"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: "id",
    header: "ID",
    cell: ({ row }) => <div>{row.getValue("id")}</div>,
  },
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
    cell: ({ row }) => <div>{row.getValue("name")}</div>,
  },
  {
    accessorKey: "email",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Email
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
    cell: ({ row }) => <div className="lowercase">{row.getValue("email")}</div>,
  },
  {
    id: "actions",
    enableHiding: false,
    cell: ({ row }) => {
      const user = row.original;

      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">メニューを開く</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              onClick={() => navigator.clipboard.writeText(user.id.toString())}
            >
              ユーザーIDをコピー
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => handleEditUser(user)}>
              ユーザー情報を編集
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => handleDeleteUser(user)}
              className="text-red-600 focus:text-red-600"
            >
              ユーザーを削除
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];

interface UserTableProps {
  data: User[];
  isLoading?: boolean;
  onUserUpdate?: (updatedUser: User) => void;
  onUserDelete?: (userId: number) => void;
  onBulkUserDelete?: (userIds: number[]) => void;
}

export function UserTable({
  data,
  isLoading = false,
  onUserUpdate,
  onUserDelete,
  onBulkUserDelete,
}: UserTableProps) {
  const [editingUser, setEditingUser] = React.useState<User | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = React.useState(false);
  const [deletingUser, setDeletingUser] = React.useState<User | null>(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = React.useState(false);
  const [isBulkDeleteDialogOpen, setIsBulkDeleteDialogOpen] =
    React.useState(false);
  const [isBulkDeleting, setIsBulkDeleting] = React.useState(false);

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setIsEditModalOpen(true);
  };

  const handleCloseEditModal = () => {
    setIsEditModalOpen(false);
    setEditingUser(null);
  };

  const handleSaveUser = (updatedUser: User) => {
    // 親コンポーネントに更新を通知
    if (onUserUpdate) {
      onUserUpdate(updatedUser);
    }
  };

  const handleDeleteUser = (user: User) => {
    // 削除確認ダイアログを表示
    setDeletingUser(user);
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async (success: boolean) => {
    if (!deletingUser) return;

    if (success) {
      // 削除成功時は親コンポーネントに通知
      if (onUserDelete) {
        onUserDelete(deletingUser.id);
      }
      setIsDeleteDialogOpen(false);
      setDeletingUser(null);
    } else {
      // 削除失敗時はダイアログを閉じる
      setIsDeleteDialogOpen(false);
      setDeletingUser(null);
      // エラーメッセージを表示する場合はここで処理
      alert("ユーザーの削除に失敗しました。");
    }
  };

  const handleCloseDeleteDialog = () => {
    setIsDeleteDialogOpen(false);
    setDeletingUser(null);
  };

  const handleBulkDelete = () => {
    const selectedRows = table.getFilteredSelectedRowModel().rows;
    if (selectedRows.length > 0) {
      setIsBulkDeleteDialogOpen(true);
    }
  };

  const handleConfirmBulkDelete = async (success: boolean) => {
    if (success) {
      // 一括削除成功時は親コンポーネントに通知
      const selectedRows = table.getFilteredSelectedRowModel().rows;
      const userIds = selectedRows.map((row) => row.original.id);
      if (onBulkUserDelete) {
        onBulkUserDelete(userIds);
      }
      // 選択をクリア
      table.toggleAllPageRowsSelected(false);
    } else {
      // 一括削除失敗時はエラーメッセージを表示
      alert("一括削除に失敗しました。");
    }
    setIsBulkDeleteDialogOpen(false);
  };

  const handleCloseBulkDeleteDialog = () => {
    setIsBulkDeleteDialogOpen(false);
    setIsBulkDeleting(false);
  };

  const columns = createColumns(handleEditUser, handleDeleteUser);
  const { table } = useUserTable(data, columns);

  // 選択された行の数を取得
  const selectedRowCount = table.getFilteredSelectedRowModel().rows.length;

  if (isLoading) {
    return (
      <div className="w-full">
        <div className="flex items-center py-4">
          <div className="h-10 w-64 animate-pulse rounded-md bg-muted"></div>
          <div className="ml-auto h-10 w-32 animate-pulse rounded-md bg-muted"></div>
        </div>
        <div className="overflow-hidden rounded-md border">
          <div className="h-96 animate-pulse bg-muted"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="flex items-center py-4">
        <Input
          placeholder="Filter emails..."
          value={(table.getColumn("email")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("email")?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />
        {selectedRowCount > 0 && (
          <Button
            variant="destructive"
            size="sm"
            onClick={handleBulkDelete}
            disabled={isBulkDeleting}
            className="ml-2"
          >
            {isBulkDeleting
              ? "削除中..."
              : `選択した${selectedRowCount}件を削除`}
          </Button>
        )}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="ml-auto">
              Columns <ChevronDown />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {table
              .getAllColumns()
              .filter((column) => column.getCanHide())
              .map((column) => {
                return (
                  <DropdownMenuCheckboxItem
                    key={column.id}
                    className="capitalize"
                    checked={column.getIsVisible()}
                    onCheckedChange={(value) =>
                      column.toggleVisibility(!!value)
                    }
                  >
                    {column.id === "id" && "ID"}
                    {column.id === "name" && "Name"}
                    {column.id === "email" && "Email"}
                  </DropdownMenuCheckboxItem>
                );
              })}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <div className="overflow-hidden rounded-md border min-w-[800px]">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="text-muted-foreground flex-1 text-sm">
          {table.getFilteredSelectedRowModel().rows.length} /{" "}
          {table.getFilteredRowModel().rows.length} rows selected.
        </div>
        <div className="space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
      <UserEditModal
        user={editingUser}
        isOpen={isEditModalOpen}
        onClose={handleCloseEditModal}
        onSave={handleSaveUser}
      />
      <UserDeleteDialog
        user={deletingUser}
        isOpen={isDeleteDialogOpen}
        onClose={handleCloseDeleteDialog}
        onConfirm={handleConfirmDelete}
        onLoadingChange={() => {}}
      />
      <UserBulkDeleteDialog
        selectedUsers={table
          .getFilteredSelectedRowModel()
          .rows.map((row) => row.original)}
        isOpen={isBulkDeleteDialogOpen}
        onClose={handleCloseBulkDeleteDialog}
        onConfirm={handleConfirmBulkDelete}
        onLoadingChange={setIsBulkDeleting}
      />
    </div>
  );
}
