package com.mik.taskplanner

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.remember
import com.mik.taskplanner.data.TaskRepository
import com.mik.taskplanner.ui.PlannerApp
import com.mik.taskplanner.ui.PlannerTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val repository = remember { TaskRepository(applicationContext) }
            DisposableEffect(repository) {
                onDispose(repository::close)
            }
            PlannerTheme {
                PlannerApp(repository)
            }
        }
    }
}

