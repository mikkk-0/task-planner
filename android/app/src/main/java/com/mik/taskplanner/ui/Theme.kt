package com.mik.taskplanner.ui

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val Background = Color(0xFF11151D)
val Surface = Color(0xFF1B202A)
val SurfaceRaised = Color(0xFF202631)
val Border = Color(0xFF343C4B)
val Purple = Color(0xFF7168EE)
val PurpleLight = Color(0xFF918AFF)
val Urgent = Color(0xFFFF6275)
val Muted = Color(0xFF9AA5B7)
val Gold = Color(0xFFF1CE73)

private val DarkColors = darkColorScheme(
    primary = PurpleLight,
    onPrimary = Color.White,
    primaryContainer = Purple,
    onPrimaryContainer = Color.White,
    secondary = Gold,
    background = Background,
    onBackground = Color(0xFFE7EAF0),
    surface = Surface,
    onSurface = Color(0xFFE7EAF0),
    surfaceVariant = SurfaceRaised,
    onSurfaceVariant = Muted,
    outline = Border,
    error = Urgent,
)

@Composable
fun PlannerTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = DarkColors, content = content)
}

