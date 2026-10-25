package com.mik.taskplanner.ui

import android.content.Context
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import com.mik.taskplanner.data.Task
import com.mik.taskplanner.data.TaskRepository

private enum class Screen(val title: String, val symbol: String) {
    TASKS("Задачи", "✓"),
    WEEK("Неделя", "▦"),
    ARCHIVE("Архив", "◷"),
}

@Composable
fun PlannerApp(repository: TaskRepository) {
    val context = LocalContext.current
    val preferences = remember(context) {
        context.getSharedPreferences("task_planner_ui", Context.MODE_PRIVATE)
    }
    val state = remember(repository, preferences) { PlannerState(repository, preferences) }
    var screen by remember { mutableStateOf(Screen.TASKS) }
    var editorVisible by remember { mutableStateOf(false) }
    var editedTask by remember { mutableStateOf<Task?>(null) }

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        bottomBar = {
            NavigationBar(containerColor = androidx.compose.ui.graphics.Color(0xFF0A0D12)) {
                Screen.entries.forEach { item ->
                    NavigationBarItem(
                        selected = screen == item,
                        onClick = { screen = item },
                        icon = { Text(item.symbol) },
                        label = { Text(item.title) },
                    )
                }
            }
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = {
                    editedTask = null
                    editorVisible = true
                },
                containerColor = Purple,
            ) { Text("＋", style = MaterialTheme.typography.headlineSmall) }
        },
    ) { padding ->
        val edit: (Task) -> Unit = {
            editedTask = it
            editorVisible = true
        }
        androidx.compose.foundation.layout.Box(modifier = Modifier.padding(padding)) {
            when (screen) {
                Screen.TASKS -> HomeScreen(state, edit)
                Screen.WEEK -> WeekScreen(state, edit)
                Screen.ARCHIVE -> ArchiveScreen(state, edit)
            }
        }
    }

    if (editorVisible) {
        TaskEditor(
            task = editedTask,
            onDismiss = { editorVisible = false },
            onSave = { title, deadline, importance, description ->
                state.save(editedTask, title, deadline, importance, description)
                editorVisible = false
            },
        )
    }
}

