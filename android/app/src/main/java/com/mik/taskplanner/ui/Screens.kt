package com.mik.taskplanner.ui

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectDragGesturesAfterLongPress
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.boundsInRoot
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.layout.positionInRoot
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.zIndex
import com.mik.taskplanner.data.Task
import java.time.DayOfWeek
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.time.temporal.TemporalAdjusters
import java.util.Locale
import kotlin.math.roundToInt

private data class DragInfo(
    val task: Task,
    val cardTopLeft: Offset,
    val pointer: Offset,
)

private data class DropHint(val toFocus: Boolean, val position: Int)

private fun insertionHint(
    pointer: Offset,
    tasks: List<Task>,
    bounds: Map<Long, Rect>,
    toFocus: Boolean,
): DropHint? {
    val cards = tasks.mapNotNull { task -> bounds[task.id] }
    if (cards.isEmpty()) return null
    val left = cards.minOf { it.left } - 40f
    val right = cards.maxOf { it.right } + 40f
    val top = cards.first().top - 24f
    val bottom = cards.last().bottom + 24f
    if (pointer.x !in left..right || pointer.y !in top..bottom) return null
    val position = cards.indexOfFirst { pointer.y < it.center.y }.let { index ->
        if (index == -1) cards.size else index
    }
    return DropHint(toFocus, position)
}

@Composable
fun HomeScreen(state: PlannerState, onEdit: (Task) -> Unit) {
    var focusDropBounds by remember { mutableStateOf<Rect?>(null) }
    var openHeaderBounds by remember { mutableStateOf<Rect?>(null) }
    var focusHeaderBounds by remember { mutableStateOf<Rect?>(null) }
    val openCardBounds = remember { mutableStateMapOf<Long, Rect>() }
    val focusCardBounds = remember { mutableStateMapOf<Long, Rect>() }
    var rootPosition by remember { mutableStateOf(Offset.Zero) }
    var dragging by remember { mutableStateOf<DragInfo?>(null) }
    var dropHint by remember { mutableStateOf<DropHint?>(null) }

    fun resolveDrop(pointer: Offset): DropHint? {
        if (focusDropBounds?.contains(pointer) == true) return DropHint(true, 0)
        insertionHint(pointer, state.openTasks, openCardBounds, false)?.let { return it }
        insertionHint(pointer, state.focusTasks, focusCardBounds, true)?.let { return it }
        if (openHeaderBounds?.contains(pointer) == true) return DropHint(false, 0)
        if (focusHeaderBounds?.contains(pointer) == true) return DropHint(true, 0)
        return null
    }

    fun updateDrag(amount: Offset) {
        val current = dragging ?: return
        val updated = current.copy(
            cardTopLeft = current.cardTopLeft + amount,
            pointer = current.pointer + amount,
        )
        dragging = updated
        dropHint = resolveDrop(updated.pointer)
    }

    fun finishDrag() {
        val drag = dragging
        val target = dropHint
        if (drag != null && target != null) {
            state.moveTask(drag.task, target.toFocus, target.position)
        }
        dragging = null
        dropHint = null
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .onGloballyPositioned { rootPosition = it.positionInRoot() }
    ) {
        Column(modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp)) {
            Text("Мои задачи", style = MaterialTheme.typography.headlineMedium)
            Text("Удерживайте карточку и перетащите её в нужное место", color = Muted)
            Spacer(Modifier.height(12.dp))
            FocusDropTarget(
                active = dropHint?.toFocus == true,
                modifier = Modifier.onGloballyPositioned { focusDropBounds = it.boundsInRoot() },
            )
            Spacer(Modifier.height(14.dp))
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(bottom = 100.dp),
                verticalArrangement = Arrangement.spacedBy(9.dp),
            ) {
                item {
                    Text(
                        "Открытые",
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier.onGloballyPositioned { openHeaderBounds = it.boundsInRoot() },
                    )
                }
                if (state.openTasks.isEmpty()) {
                    item { EmptyMessage("Все задачи выполнены или уже в фокусе") }
                }
                items(state.openTasks, key = { "open-${it.id}" }) { task ->
                    val index = state.openTasks.indexOfFirst { it.id == task.id }
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        if (dropHint == DropHint(false, index)) DropMarker()
                        DraggableTaskCard(
                            task = task,
                            onCompleted = { state.setCompleted(task, it) },
                            onEdit = { onEdit(task) },
                            onBounds = { openCardBounds[task.id] = it },
                            onStart = { topLeft, pointer ->
                                dragging = DragInfo(task, topLeft, pointer)
                                dropHint = resolveDrop(pointer)
                            },
                            onDrag = ::updateDrag,
                            onEnd = ::finishDrag,
                        )
                    }
                }
                if (state.openTasks.isNotEmpty()) {
                    item {
                        if (dropHint == DropHint(false, state.openTasks.size)) DropMarker()
                    }
                }
                item {
                    Column(
                        modifier = Modifier.onGloballyPositioned { focusHeaderBounds = it.boundsInRoot() },
                    ) {
                        Spacer(Modifier.height(8.dp))
                        HorizontalDivider(color = Border)
                        Spacer(Modifier.height(12.dp))
                        Text("Фокус", style = MaterialTheme.typography.titleMedium)
                        Text(
                            "Выполненные задачи остаются здесь",
                            color = Muted,
                            style = MaterialTheme.typography.bodySmall,
                        )
                    }
                }
                if (state.focusTasks.isEmpty()) {
                    item { EmptyMessage("Перетащите сюда самые нужные задачи") }
                }
                items(state.focusTasks, key = { "focus-${it.id}" }) { task ->
                    val index = state.focusTasks.indexOfFirst { it.id == task.id }
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        if (dropHint == DropHint(true, index)) DropMarker()
                        DraggableTaskCard(
                            task = task,
                            onCompleted = { state.setCompleted(task, it) },
                            onEdit = { onEdit(task) },
                            onBounds = { focusCardBounds[task.id] = it },
                            onStart = { topLeft, pointer ->
                                dragging = DragInfo(task, topLeft, pointer)
                                dropHint = resolveDrop(pointer)
                            },
                            onDrag = ::updateDrag,
                            onEnd = ::finishDrag,
                            focusAction = {
                                TextButton(onClick = { state.setFocus(task, false) }) { Text("Убрать") }
                            },
                        )
                    }
                }
                if (state.focusTasks.isNotEmpty()) {
                    item {
                        if (dropHint == DropHint(true, state.focusTasks.size)) DropMarker()
                    }
                }
            }
        }

        dragging?.let { drag ->
            TaskCard(
                task = drag.task,
                onCompleted = {},
                onEdit = {},
                modifier = Modifier
                    .offset {
                        IntOffset(
                            (drag.cardTopLeft.x - rootPosition.x).roundToInt(),
                            (drag.cardTopLeft.y - rootPosition.y).roundToInt(),
                        )
                    }
                    .padding(horizontal = 16.dp)
                    .graphicsLayer {
                        scaleX = 1.03f
                        scaleY = 1.03f
                        alpha = 0.92f
                        shadowElevation = 18.dp.toPx()
                    }
                    .zIndex(10f),
            )
        }
    }
}

@Composable
private fun DropMarker() {
    HorizontalDivider(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp),
        thickness = 3.dp,
        color = PurpleLight,
    )
}

@Composable
private fun FocusDropTarget(active: Boolean, modifier: Modifier = Modifier) {
    val color by animateColorAsState(if (active) Purple.copy(alpha = 0.36f) else Purple.copy(alpha = 0.12f), label = "drop")
    val border by animateColorAsState(if (active) PurpleLight else Purple.copy(alpha = 0.65f), label = "border")
    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(68.dp)
            .background(color, RoundedCornerShape(14.dp))
            .border(2.dp, border, RoundedCornerShape(14.dp)),
        contentAlignment = Alignment.Center,
    ) {
        Text(if (active) "Отпустите — задача попадёт в фокус" else "◎  Перетащите задачу сюда", color = if (active) PurpleLight else Muted)
    }
}

@Composable
private fun DraggableTaskCard(
    task: Task,
    onCompleted: (Boolean) -> Unit,
    onEdit: () -> Unit,
    onBounds: (Rect) -> Unit,
    onStart: (Offset, Offset) -> Unit,
    onDrag: (Offset) -> Unit,
    onEnd: () -> Unit,
    focusAction: (@Composable () -> Unit)? = null,
) {
    var position by remember(task.id) { mutableStateOf(Offset.Zero) }
    TaskCard(
        task = task,
        onCompleted = onCompleted,
        onEdit = onEdit,
        focusAction = focusAction,
        modifier = Modifier
            .onGloballyPositioned {
                val bounds = it.boundsInRoot()
                position = bounds.topLeft
                onBounds(bounds)
            }
            .pointerInput(task.id) {
                detectDragGesturesAfterLongPress(
                    onDragStart = { local -> onStart(position, position + local) },
                    onDrag = { change, amount ->
                        change.consume()
                        onDrag(amount)
                    },
                    onDragEnd = onEnd,
                    onDragCancel = onEnd,
                )
            },
    )
}

@Composable
fun WeekScreen(state: PlannerState, onEdit: (Task) -> Unit) {
    var weekStart by remember {
        mutableStateOf(LocalDate.now().with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY)))
    }
    val revision = state.revision
    val zone = ZoneId.systemDefault()
    val startMillis = weekStart.atStartOfDay(zone).toInstant().toEpochMilli()
    val endMillis = weekStart.plusDays(7).atStartOfDay(zone).toInstant().toEpochMilli()
    val tasks = remember(weekStart, revision) { state.weekTasks(startMillis, endMillis) }
    val byDay = tasks.groupBy { Instant.ofEpochMilli(it.deadline!!).atZone(zone).toLocalDate() }
    val rangeFormatter = DateTimeFormatter.ofPattern("d MMMM", Locale.forLanguageTag("ru"))

    Column(modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp)) {
        Text("Неделя", style = MaterialTheme.typography.headlineMedium)
        Text(
            "${weekStart.format(rangeFormatter)} — ${weekStart.plusDays(6).format(rangeFormatter)}",
            color = Muted,
        )
        Spacer(Modifier.height(10.dp))
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = { weekStart = weekStart.minusWeeks(1) }, modifier = Modifier.weight(1f)) { Text("← Прошлая") }
            TextButton(
                onClick = { weekStart = LocalDate.now().with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY)) }
            ) { Text("Сегодня") }
            Button(onClick = { weekStart = weekStart.plusWeeks(1) }, modifier = Modifier.weight(1f)) { Text("Следующая →") }
        }
        Spacer(Modifier.height(10.dp))
        LazyColumn(
            contentPadding = PaddingValues(bottom = 100.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            items((0L..6L).map(weekStart::plusDays)) { day ->
                DayRow(
                    day = day,
                    tasks = byDay[day].orEmpty(),
                    onCompleted = { task, done -> state.setCompleted(task, done) },
                    onEdit = onEdit,
                )
            }
        }
    }
}

@Composable
private fun DayRow(
    day: LocalDate,
    tasks: List<Task>,
    onCompleted: (Task, Boolean) -> Unit,
    onEdit: (Task) -> Unit,
) {
    val today = day == LocalDate.now()
    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = if (today) Purple.copy(alpha = 0.12f) else Surface,
        shape = RoundedCornerShape(14.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, if (today) Purple else Border),
    ) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    day.format(DateTimeFormatter.ofPattern("EEEE, d MMMM", Locale.forLanguageTag("ru"))).replaceFirstChar { it.uppercase() },
                    style = MaterialTheme.typography.titleSmall,
                    modifier = Modifier.weight(1f),
                )
                if (today) Text("СЕГОДНЯ", color = PurpleLight, style = MaterialTheme.typography.labelSmall)
            }
            if (tasks.isEmpty()) {
                Text("Нет задач", color = Muted, modifier = Modifier.padding(vertical = 8.dp))
            } else {
                tasks.forEach { task ->
                    TaskCard(task, { onCompleted(task, it) }, { onEdit(task) })
                }
            }
        }
    }
}

@Composable
fun ArchiveScreen(state: PlannerState, onEdit: (Task) -> Unit) {
    Column(modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp)) {
        Text("Архив", style = MaterialTheme.typography.headlineMedium)
        Text("Снимите отметку, чтобы вернуть задачу в работу", color = Muted)
        Spacer(Modifier.height(12.dp))
        LazyColumn(
            contentPadding = PaddingValues(bottom = 100.dp),
            verticalArrangement = Arrangement.spacedBy(9.dp),
        ) {
            if (state.archivedTasks.isEmpty()) item { EmptyMessage("В архиве пока пусто") }
            items(state.archivedTasks, key = { it.id }) { task ->
                TaskCard(task, { state.setCompleted(task, it) }, { onEdit(task) })
            }
        }
    }
}

@Composable
private fun EmptyMessage(text: String) {
    Box(
        modifier = Modifier.fillMaxWidth().height(74.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(text, color = Muted, style = MaterialTheme.typography.bodyMedium)
    }
}
