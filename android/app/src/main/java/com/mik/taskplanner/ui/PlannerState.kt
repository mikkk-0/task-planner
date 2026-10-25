package com.mik.taskplanner.ui

import android.content.SharedPreferences
import androidx.compose.runtime.getValue
import androidx.core.content.edit
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import com.mik.taskplanner.data.Task
import com.mik.taskplanner.data.TaskRepository

class PlannerState(
    private val repository: TaskRepository,
    private val preferences: SharedPreferences,
) {
    var openTasks by mutableStateOf<List<Task>>(emptyList())
        private set
    var focusTasks by mutableStateOf<List<Task>>(emptyList())
        private set
    var archivedTasks by mutableStateOf<List<Task>>(emptyList())
        private set
    var revision by mutableIntStateOf(0)
        private set

    init {
        refresh()
    }

    fun refresh() {
        openTasks = ordered(repository.openTasks(), OPEN_ORDER_KEY)
        focusTasks = ordered(repository.focusTasks(), FOCUS_ORDER_KEY)
        archivedTasks = repository.archivedTasks()
        revision++
    }

    fun save(task: Task?, title: String, deadline: Long?, importance: Int?, description: String) {
        if (task == null) repository.create(title, deadline, importance, description)
        else repository.update(task.id, title, deadline, importance, description)
        refresh()
    }

    fun setCompleted(task: Task, completed: Boolean) {
        repository.setCompleted(task.id, completed)
        refresh()
    }

    fun setFocus(task: Task, focused: Boolean) {
        val position = if (focused) focusTasks.size else openTasks.size
        moveTask(task, focused, position)
    }

    fun moveTask(task: Task, toFocus: Boolean, requestedPosition: Int) {
        val openOrder = openTasks.map { it.id }.filterNot { it == task.id }.toMutableList()
        val focusOrder = focusTasks.map { it.id }.filterNot { it == task.id }.toMutableList()
        val target = if (toFocus) focusOrder else openOrder
        val source = if (task.inFocus) focusTasks else openTasks
        val oldPosition = source.indexOfFirst { it.id == task.id }
        var position = requestedPosition

        if (task.inFocus == toFocus && oldPosition >= 0 && oldPosition < position) {
            position--
        }
        position = position.coerceIn(0, target.size)
        target.add(position, task.id)

        saveOrder(OPEN_ORDER_KEY, openOrder)
        saveOrder(FOCUS_ORDER_KEY, focusOrder)
        if (task.inFocus != toFocus) repository.setFocus(task.id, toFocus)
        refresh()
    }

    fun weekTasks(start: Long, end: Long): List<Task> = repository.tasksBetween(start, end)

    private fun ordered(tasks: List<Task>, key: String): List<Task> {
        val tasksById = tasks.associateBy { it.id }
        val stored = loadOrder(key).filter { it in tasksById }
        val storedIds = stored.toHashSet()
        val resultIds = stored + tasks.map { it.id }.filterNot { it in storedIds }
        saveOrder(key, resultIds)
        return resultIds.mapNotNull(tasksById::get)
    }

    private fun loadOrder(key: String): List<Long> = preferences
        .getString(key, "")
        .orEmpty()
        .split(',')
        .mapNotNull(String::toLongOrNull)

    private fun saveOrder(key: String, ids: List<Long>) {
        preferences.edit { putString(key, ids.joinToString(",")) }
    }

    private companion object {
        const val OPEN_ORDER_KEY = "open_task_order"
        const val FOCUS_ORDER_KEY = "focus_task_order"
    }
}

