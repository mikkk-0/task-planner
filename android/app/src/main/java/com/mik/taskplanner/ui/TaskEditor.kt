package com.mik.taskplanner.ui

import android.app.DatePickerDialog
import android.app.TimePickerDialog
import android.content.Context
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.mik.taskplanner.data.Task
import java.time.Instant
import java.time.ZoneId
import java.time.ZonedDateTime

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TaskEditor(
    task: Task?,
    onDismiss: () -> Unit,
    onSave: (String, Long?, Int?, String) -> Unit,
) {
    var title by remember(task?.id) { mutableStateOf(task?.title.orEmpty()) }
    var description by remember(task?.id) { mutableStateOf(task?.description.orEmpty()) }
    var deadline by remember(task?.id) { mutableStateOf(task?.deadline) }
    var importance by remember(task?.id) { mutableStateOf(task?.importance) }
    val context = LocalContext.current

    ModalBottomSheet(onDismissRequest = onDismiss, containerColor = SurfaceRaised) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .navigationBarsPadding()
                .imePadding()
                .padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Text(
                if (task == null) "Новая задача" else "Редактирование задачи",
                style = MaterialTheme.typography.headlineSmall,
            )
            OutlinedTextField(
                value = title,
                onValueChange = { title = it },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Название *") },
                singleLine = true,
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("Указать дедлайн", modifier = Modifier.weight(1f))
                Switch(
                    checked = deadline != null,
                    onCheckedChange = { enabled ->
                        deadline = if (enabled) System.currentTimeMillis() + 24 * 60 * 60 * 1000L else null
                    },
                )
            }
            if (deadline != null) {
                OutlinedButton(
                    onClick = { showDateTimePicker(context, deadline!!) { deadline = it } },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text("Дедлайн: ${formatDeadline(deadline!!)}")
                }
            }
            Text("Важность", style = MaterialTheme.typography.labelLarge, color = Muted)
            listOf(
                listOf(null to "Нет", 1 to "Низкая"),
                listOf(2 to "Средняя", 3 to "Высокая"),
            ).forEach { row ->
                Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) {
                    row.forEach { (value, label) ->
                        FilterChip(
                            selected = importance == value,
                            onClick = { importance = value },
                            label = { Text(label) },
                        )
                    }
                }
            }
            OutlinedTextField(
                value = description,
                onValueChange = { description = it },
                modifier = Modifier.fillMaxWidth().height(120.dp),
                label = { Text("Описание") },
            )
            Button(
                onClick = { onSave(title.trim(), deadline, importance, description.trim()) },
                modifier = Modifier.fillMaxWidth(),
                enabled = title.isNotBlank(),
            ) {
                Text("Сохранить")
            }
            Spacer(Modifier.height(8.dp))
        }
    }
}

private fun showDateTimePicker(context: Context, initial: Long, onPicked: (Long) -> Unit) {
    val start = Instant.ofEpochMilli(initial).atZone(ZoneId.systemDefault())
    DatePickerDialog(
        context,
        { _, year, month, day ->
            TimePickerDialog(
                context,
                { _, hour, minute ->
                    val result = ZonedDateTime.of(year, month + 1, day, hour, minute, 0, 0, ZoneId.systemDefault())
                    onPicked(result.toInstant().toEpochMilli())
                },
                start.hour,
                start.minute,
                true,
            ).show()
        },
        start.year,
        start.monthValue - 1,
        start.dayOfMonth,
    ).show()
}
