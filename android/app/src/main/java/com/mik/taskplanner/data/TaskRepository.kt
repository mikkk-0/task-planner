package com.mik.taskplanner.data

import android.content.ContentValues
import android.content.Context
import android.database.Cursor
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

class TaskRepository(context: Context) : SQLiteOpenHelper(context, "tasks.sqlite3", null, 1) {
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL(
            """
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                deadline INTEGER,
                importance INTEGER,
                description TEXT NOT NULL DEFAULT '',
                completed INTEGER NOT NULL DEFAULT 0,
                in_focus INTEGER NOT NULL DEFAULT 0,
                created_at INTEGER NOT NULL,
                completed_at INTEGER
            )
            """.trimIndent()
        )
        db.execSQL("CREATE INDEX idx_tasks_deadline ON tasks(deadline)")
        db.execSQL("CREATE INDEX idx_tasks_completed ON tasks(completed)")
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) = Unit

    fun create(title: String, deadline: Long?, importance: Int?, description: String) {
        writableDatabase.insertOrThrow("tasks", null, ContentValues().apply {
            put("title", title.trim())
            putNullable("deadline", deadline)
            putNullable("importance", importance)
            put("description", description.trim())
            put("created_at", System.currentTimeMillis())
        })
    }

    fun update(id: Long, title: String, deadline: Long?, importance: Int?, description: String) {
        writableDatabase.update("tasks", ContentValues().apply {
            put("title", title.trim())
            putNullable("deadline", deadline)
            putNullable("importance", importance)
            put("description", description.trim())
        }, "id = ?", arrayOf(id.toString()))
    }

    fun setCompleted(id: Long, completed: Boolean) {
        writableDatabase.update("tasks", ContentValues().apply {
            put("completed", if (completed) 1 else 0)
            putNullable("completed_at", if (completed) System.currentTimeMillis() else null)
        }, "id = ?", arrayOf(id.toString()))
    }

    fun setFocus(id: Long, focused: Boolean) {
        writableDatabase.update("tasks", ContentValues().apply {
            put("in_focus", if (focused) 1 else 0)
        }, "id = ?", arrayOf(id.toString()))
    }

    fun get(id: Long): Task? = query("id = ?", arrayOf(id.toString())).firstOrNull()

    fun openTasks(): List<Task> = query("completed = 0 AND in_focus = 0")

    fun focusTasks(): List<Task> = query("in_focus = 1")

    fun archivedTasks(): List<Task> = query(
        "completed = 1",
        order = "completed_at DESC, created_at DESC"
    )

    fun tasksBetween(start: Long, end: Long): List<Task> = query(
        "deadline >= ? AND deadline < ?",
        arrayOf(start.toString(), end.toString()),
        "deadline, COALESCE(importance, 0) DESC"
    )

    private fun query(
        selection: String,
        args: Array<String> = emptyArray(),
        order: String? = null,
    ): List<Task> = readableDatabase.query(
        "tasks", null, selection, args, null, null, order
    ).use { cursor -> buildList { while (cursor.moveToNext()) add(cursor.toTask()) } }

    private fun Cursor.toTask() = Task(
        id = getLong(getColumnIndexOrThrow("id")),
        title = getString(getColumnIndexOrThrow("title")),
        deadline = nullableLong("deadline"),
        importance = nullableInt("importance"),
        description = getString(getColumnIndexOrThrow("description")),
        completed = getInt(getColumnIndexOrThrow("completed")) == 1,
        inFocus = getInt(getColumnIndexOrThrow("in_focus")) == 1,
        createdAt = getLong(getColumnIndexOrThrow("created_at")),
        completedAt = nullableLong("completed_at"),
    )

    private fun Cursor.nullableLong(column: String): Long? {
        val index = getColumnIndexOrThrow(column)
        return if (isNull(index)) null else getLong(index)
    }

    private fun Cursor.nullableInt(column: String): Int? {
        val index = getColumnIndexOrThrow(column)
        return if (isNull(index)) null else getInt(index)
    }

    private fun ContentValues.putNullable(key: String, value: Long?) {
        if (value == null) putNull(key) else put(key, value)
    }

    private fun ContentValues.putNullable(key: String, value: Int?) {
        if (value == null) putNull(key) else put(key, value)
    }
}

