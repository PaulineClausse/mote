//! Horloge mote : `CLOCK_MONOTONIC` du casque, seul référentiel de temps (SPEC-64c5 §9.3).

/// Temps courant de l'horloge mote, en nanosecondes.
#[cfg(unix)]
pub fn now_ns() -> i64 {
    let mut ts = libc::timespec {
        tv_sec: 0,
        tv_nsec: 0,
    };
    // SAFETY: ts est un timespec valide ; CLOCK_MONOTONIC existe sur Linux et Android.
    let rc = unsafe { libc::clock_gettime(libc::CLOCK_MONOTONIC, &mut ts) };
    debug_assert_eq!(rc, 0);
    ts.tv_sec as i64 * 1_000_000_000 + ts.tv_nsec as i64
}

/// Hors Unix (tests sur PC Windows), une horloge monotone ancrée au premier appel suffit.
#[cfg(not(unix))]
pub fn now_ns() -> i64 {
    use std::sync::OnceLock;
    use std::time::Instant;
    static ORIGIN: OnceLock<Instant> = OnceLock::new();
    ORIGIN.get_or_init(Instant::now).elapsed().as_nanos() as i64
}

#[cfg(test)]
mod tests {
    use super::now_ns;

    #[test]
    fn monotone() {
        let a = now_ns();
        let b = now_ns();
        assert!(a >= 0 && b >= a);
    }
}
