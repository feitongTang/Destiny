import AVFoundation
import Foundation

guard CommandLine.arguments.count == 3 else {
    fputs("usage: render_score_realtime.swift score.json output.wav\n", stderr)
    exit(2)
}

struct ScoreNote: Decodable {
    let start: Double
    let duration: Double
    let pitch: UInt8
    let velocity: UInt8
    let voice: String
}

struct Score: Decodable {
    let bpm: Double
    let totalBeats: Double
    let notes: [ScoreNote]
}

struct TimedEvent {
    let seconds: Double
    let isNoteOn: Bool
    let pitch: UInt8
    let velocity: UInt8
    let voice: String
}

let scoreURL = URL(fileURLWithPath: CommandLine.arguments[1])
let outputURL = URL(fileURLWithPath: CommandLine.arguments[2])
let instrumentURL = URL(fileURLWithPath: "/Library/Application Support/Logic/Sampler Instruments/z_Internal/Studio Piano/Studio Grand Piano.exs")
let score = try JSONDecoder().decode(Score.self, from: Data(contentsOf: scoreURL))
let secondsPerBeat = 60.0 / score.bpm

let engine = AVAudioEngine()
let zhu = AVAudioUnitSampler()
let liang = AVAudioUnitSampler()
let accompaniment = AVAudioUnitSampler()
let submixer = AVAudioMixerNode()
let reverb = AVAudioUnitReverb()

for node in [zhu, liang, accompaniment] { engine.attach(node) }
engine.attach(submixer)
engine.attach(reverb)
for sampler in [zhu, liang, accompaniment] { try sampler.loadInstrument(at: instrumentURL) }

zhu.volume = 0.92
zhu.pan = 0.12
liang.volume = 0.88
liang.pan = -0.12
accompaniment.volume = 0.52
reverb.loadFactoryPreset(.mediumRoom)
reverb.wetDryMix = 10

engine.connect(zhu, to: submixer, format: nil)
engine.connect(liang, to: submixer, format: nil)
engine.connect(accompaniment, to: submixer, format: nil)
engine.connect(submixer, to: reverb, format: nil)
engine.connect(reverb, to: engine.mainMixerNode, format: nil)
engine.mainMixerNode.outputVolume = 0

let tapFormat = reverb.outputFormat(forBus: 0)
var audioFile: AVAudioFile? = try AVAudioFile(forWriting: outputURL, settings: tapFormat.settings)
let writeQueue = DispatchQueue(label: "destiny.audio.write")
var writeError: Error?
reverb.installTap(onBus: 0, bufferSize: 2048, format: tapFormat) { buffer, _ in
    writeQueue.sync {
        do { try audioFile?.write(from: buffer) } catch { writeError = error }
    }
}

func sampler(for voice: String) -> AVAudioUnitSampler {
    switch voice {
    case "zhu": return zhu
    case "liang": return liang
    default: return accompaniment
    }
}

var events: [TimedEvent] = []
for note in score.notes {
    events.append(TimedEvent(seconds: note.start * secondsPerBeat, isNoteOn: true,
                             pitch: note.pitch, velocity: note.velocity, voice: note.voice))
    events.append(TimedEvent(seconds: (note.start + note.duration * 0.98) * secondsPerBeat,
                             isNoteOn: false, pitch: note.pitch, velocity: 0, voice: note.voice))
}
events.sort {
    if $0.seconds != $1.seconds { return $0.seconds < $1.seconds }
    return !$0.isNoteOn && $1.isNoteOn
}

try engine.start()
let clock = ContinuousClock()
let start = clock.now
for event in events {
    let target = start.advanced(by: .seconds(event.seconds))
    if clock.now < target { try await clock.sleep(until: target) }
    let targetSampler = sampler(for: event.voice)
    if event.isNoteOn {
        targetSampler.startNote(event.pitch, withVelocity: event.velocity, onChannel: 0)
    } else {
        targetSampler.stopNote(event.pitch, onChannel: 0)
    }
}
let end = start.advanced(by: .seconds(score.totalBeats * secondsPerBeat + 2.0))
if clock.now < end { try await clock.sleep(until: end) }

engine.stop()
reverb.removeTap(onBus: 0)
writeQueue.sync {}
audioFile = nil
if let error = writeError { throw error }
print(outputURL.path)
