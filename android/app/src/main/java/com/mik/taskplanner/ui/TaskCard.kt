package com.mik.taskplanner.ui

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.unit.dp
import com.mik.taskplanner.data.Task
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

private val deadlineFormatter = DateTimeFormatter.ofPattern("dd.MM.yyyy · HH:mm", Locale.forLanguageTag("ru"))

@Composable
fun TaskCard(
    task: Task,
    onCompleted: (Boolean) -> Unit,
    onEdit: () -> Unit,
    modifier: Modifier = Modifier,
    focusAction: (@Composable () -> Unit)? = null,
) {
    val container by animateColorAsState(
        if (task.completed) Surface.copy(alpha = 0.65f) else Surface,
        label = "task color"
    )
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable(onClick = onEdit),
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = container),
        border = CardDefaults.outlinedCardBorder(),
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 10.dp),
            verticalAlignment = Alignment.Top,
        ) {
            Checkbox(checked = task.completed, onCheckedChange = onCompleted)
            Spacer(Modifier.width(8.dp))
            Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(
                    text = task.title,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.SemiBold,
                    color = if (task.completed) Muted else MaterialTheme.colorScheme.onSurface,
                    textDecoration = if (task.completed) TextDecoration.LineThrough else null,
                )
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                    task.deadline?.let { deadline ->
                        val urgent = deadline <= System.currentTimeMillis() + 48 * 60 * 60 * 1000L
                        Text(
                            formatDeadline(deadline),
                            style = MaterialTheme.typography.labelMedium,
                            color = if (urgent) Urgent else Muted,
                            fontWeight = if (urgent) FontWeight.Bold else FontWeight.Normal,
                        )
                    }
                    task.importance?.let {
                        Text(
                            importanceName(it),
                            modifier = Modifier
                                .padding(horizontal = 2.dp)
                                .padding(horizontal = 6.dp, vertical = 2.dp),
                            style = MaterialTheme.typography.labelMedium,
                            color = Gold,
                        )
                    }
                }
                if (task.description.isNotBlank()) {
                    Text(task.description, style = MaterialTheme.typography.bodySmall, color = Muted, maxLines = 2)
                }
            }
            focusAction?.invoke()
        }
    }
}

fun formatDeadline(value: Long): String = Instant.ofEpochMilli(value)
    .atZone(ZoneId.systemDefault())
    .format(deadlineFormatter)

fun importanceName(value: Int?): String = when (value) {
    1 -> "Низкая"
    2 -> "Средняя"
    3 -> "Высокая"
    else -> "Не указана"
}
