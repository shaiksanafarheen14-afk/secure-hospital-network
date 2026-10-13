"""Performance calculation engine for network transmissions.

Computes latency, jitter, throughput, packet loss rate, and transmission success metrics.
Strictly decoupled from GUI components for testability.
"""

from typing import List, Optional

try:
    from core.models import TransmissionResult, DeliveryStatus, NetworkMetricsSummary
except (ImportError, ValueError):
    from .models import TransmissionResult, DeliveryStatus, NetworkMetricsSummary


def calculate_loss_rate(total_sent: int, total_lost: int) -> float:
    """Calculate packet loss percentage."""
    if total_sent <= 0:
        return 0.0
    return round((total_lost / total_sent) * 100.0, 2)


def calculate_success_rate(total_sent: int, total_delivered: int) -> float:
    """Calculate transmission success percentage."""
    if total_sent <= 0:
        return 0.0
    return round((total_delivered / total_sent) * 100.0, 2)


def calculate_throughput(total_delivered_bytes: int, duration_seconds: float) -> float:
    """Calculate network throughput in kilobits per second (kbps)."""
    if duration_seconds <= 0 or total_delivered_bytes <= 0:
        return 0.0
    # (bytes * 8 bits) / 1000 = kilobits
    kilobits = (total_delivered_bytes * 8) / 1000.0
    return round(kilobits / duration_seconds, 2)


def calculate_jitter(delays_ms: List[float]) -> float:
    """Calculate statistical jitter (delay variance) in milliseconds."""
    if len(delays_ms) < 2:
        return 0.0
    diffs = [abs(delays_ms[i] - delays_ms[i - 1]) for i in range(1, len(delays_ms))]
    return round(sum(diffs) / len(diffs), 2)


def compute_metrics_summary(
    results: List[TransmissionResult],
    simulated_duration_seconds: float = 0.0
) -> NetworkMetricsSummary:
    """Compute aggregate statistical performance summary from transmission records."""
    if not results:
        return NetworkMetricsSummary()

    total_sent = len(results)
    delivered = [r for r in results if r.delivery_status == DeliveryStatus.DELIVERED]
    total_delivered = len(delivered)
    total_lost = sum(1 for r in results if r.delivery_status == DeliveryStatus.LOST)
    total_retransmitted = sum(r.retransmissions for r in results)
    total_corrupted = sum(1 for r in results if "corrupt" in r.crc_status.lower() or r.delivery_status == DeliveryStatus.CORRUPTED)

    success_rate = calculate_success_rate(total_sent, total_delivered)

    delays = [r.latency_ms for r in delivered if r.latency_ms >= 0]
    if delays:
        avg_delay = round(sum(delays) / len(delays), 2)
        min_delay = round(min(delays), 2)
        max_delay = round(max(delays), 2)
        jitter = calculate_jitter(delays)
    else:
        avg_delay = 0.0
        min_delay = 0.0
        max_delay = 0.0
        jitter = 0.0

    # Total bytes successfully delivered
    total_delivered_bytes = sum(r.frame_size_bytes for r in delivered)

    # Estimate duration: either explicitly supplied or sum of latencies in seconds
    if simulated_duration_seconds > 0:
        duration = simulated_duration_seconds
    else:
        # Sum of delays converted to seconds, or default 1 second baseline
        duration = max(sum(r.latency_ms for r in results) / 1000.0, 0.5)

    throughput_kbps = calculate_throughput(total_delivered_bytes, duration)
    throughput_pps = round(total_delivered / duration, 2) if duration > 0 else 0.0

    return NetworkMetricsSummary(
        total_sent=total_sent,
        total_received=total_delivered,
        total_lost=total_lost,
        total_retransmitted=total_retransmitted,
        total_corrupted=total_corrupted,
        success_rate_percent=success_rate,
        average_delay_ms=avg_delay,
        throughput_kbps=throughput_kbps,
        throughput_pps=throughput_pps,
        min_delay_ms=min_delay,
        max_delay_ms=max_delay,
        jitter_ms=jitter
    )
