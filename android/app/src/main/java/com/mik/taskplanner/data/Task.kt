package com.mik.taskplanner.data

data class Task(
    val id: Long,
    val title: String,
    val deadline: Long?,
    val importance: Int?,
    val description: String,
    val completed: Boolean,
    val inFocus: Boolean,
    val createdAt: Long,
    val completedAt: Long?,
)

